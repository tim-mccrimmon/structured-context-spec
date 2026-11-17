"""`scs bundle diff` (RFC 0002 section 7, D-41). Registered on the `bundle` group; the function
is not named `diff`, so command discovery does not also add it at the top level."""

from pathlib import Path
from typing import Optional

import click
from scs_validator.envelope import relative
from scs_validator.resolver import find_project_root

from scs_tools import bundle_diff
from scs_tools.commands.bundle import ROOT_BUNDLE_FILES, bundle
from scs_tools.machine import EXIT_FILE, EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.versioning import VERSION_RE
from scs_tools.workspace import find_workspace, repository_root


@bundle.command("diff")
@click.argument("bundle_file", required=False, type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "--from",
    "from_version",
    default=None,
    help="The version to compare from (default: the latest version, else empty)",
)
@click.option(
    "--to",
    "to_version",
    default=bundle_diff.WORKING,
    show_default=True,
    help="A version, or 'working' for the working tree",
)
@machine_command("bundle diff")
def bundle_diff_command(
    envelope: Envelope,
    out: Output,
    bundle_file: Optional[Path],
    from_version: Optional[str],
    to_version: str,
) -> None:
    """
    Show what changed in a bundle between two versions

    Compares a version with the working tree (the default) or with another version: SCDs
    added and removed; prohibitions, directives, and facts added, removed, and changed;
    citations added and removed; imports added, removed, and re-pinned, across the bundle's
    whole tree. A version's content comes from its tag. With no version yet, everything is
    added. The output is deterministic. Writes nothing.

    \b
    Examples:
        scs bundle diff                                  # root bundle, latest version -> working
        scs bundle diff bundles/concepts/security.yaml --from 1.0.0
        scs bundle diff --from 1.0.0 --to 1.1.0 --json
    """
    for value in (from_version, None if to_version == bundle_diff.WORKING else to_version):
        if value is not None and not VERSION_RE.match(value):
            raise CommandError(
                "VERSION_INVALID",
                f"{value} is not MAJOR.MINOR.PATCH (or 'working' for --to)",
                exit_code=EXIT_USAGE,
            )
    if bundle_file is None:
        found = [Path.cwd() / "bundles" / name for name in ROOT_BUNDLE_FILES]
        found = [path for path in found if path.exists()]
        if len(found) != 1:
            raise CommandError(
                "NO_INPUT",
                "Name the bundle to diff (no single root bundle here)",
                exit_code=EXIT_USAGE,
            )
        bundle_file = found[0]
    if not bundle_file.is_file():
        raise CommandError(
            "FILE_NOT_FOUND", f"No such bundle file: {bundle_file}", exit_code=EXIT_FILE
        )

    root = repository_root(bundle_file.parent) or find_project_root(bundle_file)
    workspace_root = find_workspace(bundle_file.resolve().parent) or find_project_root(bundle_file)
    try:
        bundle_id, old, new = bundle_diff.sides(
            envelope, bundle_file, workspace_root, from_version, to_version
        )
    except bundle_diff.DiffFailed:
        envelope.result = {"diffed": False}
        return
    result = bundle_diff.diff(old.content, new.content)

    def side(s: bundle_diff.Side) -> dict:
        entry = {"version": s.label, "source": s.source}
        if s.tag:
            entry["tag"] = s.tag
        if s.path:
            entry["path"] = relative(s.path, root)
        return entry

    envelope.result = {
        "diffed": True,
        "bundle": bundle_id,
        "from": side(old),
        "to": side(new),
        **result,
    }
    for line in bundle_diff.summary_lines(bundle_id, old, new, result):
        out.echo(line)
