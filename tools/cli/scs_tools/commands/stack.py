"""`scs stack` (RFC 0002 section 13, D-67): preview a stack of compiled artifacts. Reads only."""

from pathlib import Path
from typing import Tuple

import click
from scs_validator.envelope import EXIT_FILE, Diagnostic, relative
from scs_validator.utils import resolve_schema_dir

from scs_tools import stacks
from scs_tools.machine import CommandError, Envelope, Output, machine_command


@click.command()
@click.argument(
    "artifacts", nargs=-1, required=True, type=click.Path(dir_okay=False, path_type=Path)
)
@click.option("--strict", is_flag=True, help="Treat warnings as errors (exit code 2)")
@machine_command("stack")
def stack(envelope: Envelope, out: Output, artifacts: Tuple[Path, ...], strict: bool) -> None:
    """
    Preview a stack of compiled artifacts loaded together

    Give the artifacts in the order a client loads them, outermost layer first. Shows each
    layer, every rule and fact of the combined context in stack order with the layer it came
    from, and what can be checked exactly: a bundle in two layers (error), a directive that
    mentions what another layer prohibits (warning), identical text in two layers, and DRAFT
    layers. Rules are never merged, reordered, or dropped; SCS defines no precedence between
    layers. Reads only.

    \b
    Examples:
        scs stack ~/jdoe-context/domain/dist/jdoe-1.0.0.yaml dist/medtech-cdmo-1.2.0.yaml
        scs stack global.yaml projects/infusion-pump-fw.yaml --json
    """
    schema_dir, searched = resolve_schema_dir(None)
    if schema_dir is None:
        raise CommandError(
            "SCHEMA_DIR_NOT_FOUND", f"No SCS schema directory found (searched {searched})"
        )

    cwd = Path.cwd()
    layers = []
    for position, path in enumerate(artifacts, start=1):
        shown = relative(path, cwd)
        if not path.is_file():
            raise CommandError(
                "FILE_NOT_FOUND", f"No such artifact: {shown}", exit_code=EXIT_FILE, path=shown
            )
        try:
            artifact = stacks.read(path, shown, schema_dir)
        except OSError as e:
            raise CommandError(
                "FILE_UNREADABLE",
                f"{shown} could not be read: {e}",
                exit_code=EXIT_FILE,
                path=shown,
            )
        except ValueError as e:
            envelope.error("STACK_ARTIFACT_INVALID", str(e), shown)
            continue
        layers.append(stacks.Layer(position, path, shown, artifact))
    if envelope.has_errors():
        envelope.result = {"stacked": False}
        return

    for finding in stacks.check(layers):
        envelope.diagnostics.append(
            Diagnostic(finding.severity, finding.code, finding.message, finding.path)
        )

    combined = stacks.context(layers)
    envelope.result = {
        "stacked": True,
        "layers": [
            {
                "position": layer.position,
                "path": layer.shown,
                "id": layer.id,
                "type": layer.artifact["type"],
                "version": layer.version,
                **(
                    {"source_digest": layer.artifact["source_digest"]}
                    if layer.artifact.get("source_digest")
                    else {}
                ),
            }
            for layer in layers
        ],
        "context": combined,
    }

    out.echo(f"Stack of {len(layers)} layer{'s' if len(layers) != 1 else ''}, outermost first:")
    for layer in layers:
        digest = layer.artifact.get("source_digest")
        out.echo(
            f"  {layer.position}. {layer.id} {layer.version} ({layer.artifact['type']})"
            + (f"  {digest}" if digest else "")
            + f"  {layer.shown}"
        )
    for layer in layers:
        out.echo(f"\nLayer {layer.position}: {layer.id} {layer.version}")
        for entry in combined:
            if entry["layer"] == layer.position:
                kind, text = ("rule", entry["rule"]) if "rule" in entry else ("fact", entry["fact"])
                out.echo(f"  [{kind}] {entry['id']}: {text}")
