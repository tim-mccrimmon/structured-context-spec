"""
Compile command - build a runtime artifact from a Domain or Project bundle
"""

import hashlib
from pathlib import Path
from typing import Optional

import click
import yaml
from scs_validator import api, integrity
from scs_validator.envelope import Change, diagnostics_from_results, relative
from scs_validator.gitrepo import GitRepo, GitUnavailable
from scs_validator.names import bundle_name, version_tag
from scs_validator.resolver import find_project_root, resolve
from scs_validator.utils import ValidationResult

from scs_tools.compiler import compile_tree, render
from scs_tools.machine import EXIT_FILE, EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.workspace import (
    find_domain_repository,
    find_workspace,
    repository_root,
    within,
    workspace_name,
)


@click.command()
@click.argument("bundle_file", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write the artifact here (default: dist/<bundle-name>-<version>.yaml in the workspace)",
)
@click.option(
    "--stdout",
    "to_stdout",
    is_flag=True,
    help="Write the artifact to stdout instead of a file (not with --json)",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    show_default=True,
    help="Artifact serialization",
)
@click.option(
    "--version",
    "version",
    help="Compile this released version from its tag, with its source_digest (D-57)",
)
@click.option(
    "--allow-draft",
    is_flag=True,
    help="Compile DRAFT bundles; the artifact version becomes DRAFT+<digest>",
)
@click.option("--no-cites", is_flag=True, help="Leave standard citations out of the artifact")
@click.option("--no-validate", is_flag=True, help="Skip validation before compiling")
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing")
@machine_command("compile")
def compile(
    envelope: Envelope,
    out: Output,
    bundle_file: Path,
    output: Path,
    to_stdout: bool,
    fmt: str,
    version: Optional[str],
    allow_draft: bool,
    no_cites: bool,
    no_validate: bool,
    dry_run: bool,
) -> None:
    """
    Compile a Domain or Project bundle into a runtime artifact

    The artifact is one self-contained file holding the bundle's prohibitions and directives
    as rules with stable ids, its facts, a version, and a self-identification rule. It
    contains no timestamps or other volatile content, so the same source always produces the
    same bytes and hash. It is written to the workspace's dist/ directory as
    <bundle-name>-<version>.yaml unless --output or --stdout says otherwise.
    See spec/0.7/runtime-artifact.md.

    With --version, the released version is compiled from its tag, so the working tree's
    edits since then do not enter it. Without it, the working bundle is compiled, and a DRAFT
    one needs --allow-draft. Either way, every versioned bundle it pins must match its tag.

    \b
    Examples:
        scs compile bundles/domain-bundle.yaml --version 1.0.0
        scs compile bundles/project-bundle.yaml --allow-draft
        scs compile bundles/project-bundle.yaml --version 1.0.0 --stdout
    """
    if to_stdout and (out.machine or output or dry_run):
        raise CommandError(
            "USAGE_ERROR",
            "--stdout cannot be combined with --json, --output, or --dry-run",
            exit_code=EXIT_USAGE,
        )
    if not bundle_file.is_file():
        raise CommandError(
            "FILE_NOT_FOUND", f"No such bundle file: {bundle_file}", exit_code=EXIT_FILE
        )

    root = repository_root(bundle_file.parent) or find_project_root(bundle_file)
    workspace_root = find_workspace(bundle_file.resolve().parent) or find_project_root(bundle_file)

    if version is not None:
        result = _compile_version(envelope, bundle_file, workspace_root, version, not no_cites)
        if result is None:
            envelope.result = {"compiled": False}
            return
        _write(
            envelope,
            out,
            result,
            bundle_file,
            root,
            workspace_root,
            output,
            to_stdout,
            fmt,
            dry_run,
        )
        return

    if not no_validate:
        try:
            report = api.validate_bundle(bundle_file)
        except api.SchemaDirNotFound:
            raise CommandError(
                "SCHEMA_DIR_NOT_FOUND",
                "Schema directory not found; set SCS_SCHEMA_DIR",
                exit_code=EXIT_FILE,
            )
        if report.exit_code() == 1:
            envelope.diagnostics.extend(
                d for d in diagnostics_from_results(report.all_results()) if d.severity == "error"
            )
            envelope.result = {"compiled": False}
            out.echo("Validation failed; nothing compiled.", err=True)
            return

    tree = resolve(bundle_file)
    integrity_result = _check_pinned(tree, workspace_root)
    if integrity_result.errors:
        envelope.diagnostics.extend(diagnostics_from_results([integrity_result]))
        envelope.result = {"compiled": False}
        return
    result = compile_tree(tree, allow_draft=allow_draft, include_cites=not no_cites)
    _write(
        envelope, out, result, bundle_file, root, workspace_root, output, to_stdout, fmt, dry_run
    )


def _check_pinned(tree, workspace_root: Path):
    """Pinned versions in the tree match their tags (D-16), in a git repository."""
    try:
        repo = GitRepo.find(workspace_root)
    except GitUnavailable:
        repo = None
    if repo is None:
        return ValidationResult("versions")
    with repo:
        return integrity.check_pinned(
            tree, repo, workspace_name(workspace_root), workspace_root, require_tags=False
        )


def _compile_version(
    envelope: Envelope, bundle_file: Path, workspace_root: Path, version: str, include_cites: bool
):
    """Compile a released version from its tag (D-57), after check 1 for that tag (D-39)."""
    data = yaml.safe_load(bundle_file.read_text(encoding="utf-8")) or {}
    name = bundle_name(str(data.get("id", "")), bundle_file)
    tag = version_tag(workspace_name(workspace_root), name, version)
    domain_repo = find_domain_repository(workspace_root)
    if domain_repo is None:
        raise CommandError(
            "VERSION_NOT_FOUND",
            f"--version reads a version tag; {workspace_root} is not in a Domain repository",
        )
    try:
        repo = GitRepo.find(domain_repo)
    except GitUnavailable as e:
        raise CommandError("GIT_REQUIRED", f"--version reads the version's tag: {e}")
    if repo is None:
        raise CommandError(
            "GIT_REQUIRED", f"--version reads the version's tag; {workspace_root} is not in git"
        )
    with repo:
        found = [t for t in repo.version_tags() if t.tag == tag]
        if not found:
            raise CommandError(
                "VERSION_NOT_FOUND", f"No tag {tag}: {data.get('id')} {version} was not released"
            )
        checked = ValidationResult("versions")
        tagged = integrity.verify_tag(repo, found[0], checked)
        if tagged is None or tagged.tree is None:
            envelope.diagnostics.extend(diagnostics_from_results([checked]))
            return None
        return compile_tree(tagged.tree, include_cites=include_cites)


def _write(
    envelope, out, result, bundle_file, root, workspace_root, output, to_stdout, fmt, dry_run
):
    for warning in result.warnings:
        envelope.warning("COMPILE_WARNING", warning)
    if result.errors or result.artifact is None:
        for error in result.errors:
            envelope.error("COMPILE_ERROR", error)
        envelope.result = {"compiled": False}
        return

    artifact = result.artifact
    text = render(artifact, fmt)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    rule_count = len(artifact["rules"]) - 1
    fact_count = len(artifact.get("facts", []))
    summary = (
        f"Compiled {artifact['id']} {artifact['version']}: "
        f"{rule_count} rules, {fact_count} facts, sha256 {digest}"
    )

    if to_stdout:
        click.echo(text, nl=False)
        click.echo(summary, err=True)
        return

    target = output or (
        workspace_root / "dist" / f"{bundle_name(str(artifact['id']))}-{artifact['version']}.{fmt}"
    )
    shown = relative(target, root)
    if not within(target, root):
        raise CommandError(
            "OUTPUT_OUTSIDE_REPO",
            f"{target} is outside the repository ({root}); compile output stays inside it",
            path=shown,
        )

    data = text.encode("utf-8")
    if not (target.is_file() and target.read_bytes() == data):
        envelope.changes.append(Change("modify" if target.exists() else "create", path=shown))
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    envelope.result = {
        "compiled": True,
        "path": shown,
        "id": artifact["id"],
        "version": artifact["version"],
        "sha256": digest,
        "source_digest": artifact.get("source_digest"),
    }
    out.echo(f"{summary} -> {shown}" + (" (dry run, nothing written)" if dry_run else ""))
