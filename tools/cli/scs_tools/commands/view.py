"""View command - write a review package for a Domain or Project bundle"""

import hashlib
from contextlib import ExitStack
from pathlib import Path
from typing import Optional

import click
import yaml
from scs_validator.digest import find_version_manifest
from scs_validator.envelope import Change, diagnostics_from_results, relative
from scs_validator.gitrepo import GitRepo, GitUnavailable, split_version
from scs_validator.integrity import verify_tag
from scs_validator.names import bundle_name, version_tag
from scs_validator.resolver import find_project_root, resolve
from scs_validator.utils import ValidationResult

from scs_tools import view as review
from scs_tools.machine import EXIT_FILE, EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.workspace import (
    find_domain_repository,
    find_workspace,
    repository_root,
    within,
    workspace_name,
)


@click.command()
@click.argument("bundle_file", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--version", "version", help="Show this released version, read from its tag")
@click.option("--allow-draft", is_flag=True, help="Show a DRAFT bundle (marked not for approval)")
@click.option(
    "--domain",
    "domain_file",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Domain bundle file to show as inherited (default: the repository's Domain)",
)
@click.option("--domain-version", help="Domain version to show (default: the latest released)")
@click.option("--no-domain", is_flag=True, help="Leave the inherited Domain out")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write the package here (default: dist/<bundle-name>-<version>-review.html)",
)
@click.option("--open", "open_after", is_flag=True, help="Open the package in a browser")
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing")
@machine_command("view")
def view(
    envelope: Envelope,
    out: Output,
    bundle_file: Path,
    version: Optional[str],
    allow_draft: bool,
    domain_file: Optional[Path],
    domain_version: Optional[str],
    no_domain: bool,
    output: Optional[Path],
    open_after: bool,
    dry_run: bool,
) -> None:
    """
    Write a review package for a Domain or Project bundle

    The package is one self-contained HTML file for the people who review and certify the
    bundle. It shows the release (version, content digest and whether it matches, approver),
    a summary built from counts, a contents tree, and every prohibition, rule, and fact
    verbatim with its id, source, citations, and the exact line the AI receives. A Project's
    package also shows its Domain's rules, marked as inherited: by default the Domain's
    latest released version in the same repository. Nothing in it is written by AI, and it
    holds no timestamps of its own, so the same source always produces the same file.

    With --version, the released version is read from its tag. Without it, the working
    bundle is shown, and a DRAFT one needs --allow-draft and is marked as not for approval.

    \b
    Examples:
        scs view bundles/project-bundle.yaml --version 1.0.0 --open
        scs view bundles/domain-bundle.yaml --allow-draft
        scs view bundles/project-bundle.yaml --version 0.3.0 --domain-version 1.2.0
    """
    if no_domain and (domain_file or domain_version):
        raise CommandError(
            "USAGE_ERROR",
            "--no-domain cannot be combined with --domain or --domain-version",
            exit_code=EXIT_USAGE,
        )
    if domain_file and domain_version:
        raise CommandError(
            "USAGE_ERROR",
            "--domain shows a working Domain bundle; --domain-version reads a released one. "
            "Use one",
            exit_code=EXIT_USAGE,
        )
    if not bundle_file.is_file():
        raise CommandError(
            "FILE_NOT_FOUND", f"No such bundle file: {bundle_file}", exit_code=EXIT_FILE
        )

    root_dir = repository_root(bundle_file.parent) or find_project_root(bundle_file)
    workspace_root = find_workspace(bundle_file.resolve().parent) or find_project_root(bundle_file)
    domain_repo = find_domain_repository(workspace_root)

    with ExitStack() as stack:
        repo = _repo(domain_repo or workspace_root, stack)
        if version is not None:
            data = yaml.safe_load(bundle_file.read_text(encoding="utf-8")) or {}
            name = bundle_name(str(data.get("id", "")), bundle_file)
            root = _released(envelope, repo, workspace_name(workspace_root), name, version)
        else:
            tree = resolve(bundle_file)
            root = review.Source(tree, workspace_root, _manifest(tree))
        if root is None:
            envelope.result = {"written": False}
            return

        domain = None
        if root.tree.root.type == "project" and not no_domain:
            domain = _domain(envelope, repo, domain_repo, domain_file, domain_version)
            if domain is None and envelope.has_errors():
                envelope.result = {"written": False}
                return

        result = review.build_view(root, domain, allow_draft=allow_draft)
        for warning in result.warnings:
            envelope.warning("COMPILE_WARNING", warning)
        if result.errors or result.view is None:
            for error in result.errors:
                envelope.error("COMPILE_ERROR", error)
            envelope.result = {"written": False}
            return
        text = review.render_html(result.view)

    layer = result.view["layers"][-1]
    release = layer["release"]
    target = output or (
        workspace_root / "dist" / f"{bundle_name(layer['id'])}-{release['version']}-review.html"
    )
    shown = relative(target, root_dir) if within(target, root_dir) else str(target)
    data = text.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    if not (target.is_file() and target.read_bytes() == data):
        envelope.changes.append(Change("modify" if target.exists() else "create", path=shown))
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    prohibitions, rules, facts = review.counts(result.view)
    inherited = result.view["layers"][0] if len(result.view["layers"]) > 1 else None
    envelope.result = {
        "written": not dry_run,
        "path": shown,
        "id": layer["id"],
        "version": release["version"],
        "source_digest": release.get("source_digest"),
        "verified": release["verified"],
        "draft": release["draft"],
        "domain": (
            {"id": inherited["id"], "version": inherited["release"]["version"]}
            if inherited
            else None
        ),
        "sha256": digest,
    }
    out.echo(
        f"Review package for {layer['id']} {release['version']}: {prohibitions} prohibitions, "
        f"{rules} rules, {facts} facts"
        + (
            f", with Domain {inherited['id']} {inherited['release']['version']}"
            if inherited
            else ""
        )
        + f" -> {shown}"
        + (" (dry run, nothing written)" if dry_run else "")
    )
    if open_after and not dry_run and not out.machine:
        click.launch(str(target))


def _repo(start: Path, stack: ExitStack) -> Optional[GitRepo]:
    try:
        repo = GitRepo.find(start)
    except GitUnavailable:
        return None
    return stack.enter_context(repo) if repo is not None else None


def _manifest(tree) -> Optional[dict]:
    if tree.root.version in (None, "", "DRAFT"):
        return None
    found = find_version_manifest(tree.root)
    return found[1] if found else None


def _released(
    envelope: Envelope, repo: Optional[GitRepo], workspace: str, name: str, version: str
) -> Optional[review.Source]:
    """A released version read from its tag, after check 1 for that tag (D-39)."""
    tag = version_tag(workspace, name, version)
    if repo is None:
        raise CommandError("GIT_REQUIRED", f"--version reads the tag {tag}; this is not in git")
    found = [t for t in repo.version_tags() if t.tag == tag]
    if not found:
        raise CommandError("VERSION_NOT_FOUND", f"No tag {tag}: version {version} was not released")
    checked = ValidationResult("versions")
    tagged = verify_tag(repo, found[0], checked)
    if tagged is None or tagged.tree is None:
        envelope.diagnostics.extend(diagnostics_from_results([checked]))
        return None
    return review.Source(tagged.tree, tagged.root, tagged.manifest, tag)


def _domain(
    envelope: Envelope,
    repo: Optional[GitRepo],
    domain_repo: Optional[Path],
    domain_file: Optional[Path],
    domain_version: Optional[str],
) -> Optional[review.Source]:
    """The Domain to show as inherited: a given file, else the repository's released Domain
    (the latest, or --domain-version), as Project review does (D-89)."""
    if domain_file is not None:
        if not domain_file.is_file():
            raise CommandError(
                "FILE_NOT_FOUND", f"No such Domain bundle file: {domain_file}", exit_code=EXIT_FILE
            )
        tree = resolve(domain_file)
        if tree.root.type != "domain":
            raise CommandError(
                "USAGE_ERROR",
                f"--domain names {tree.root.id}, a {tree.root.type} bundle, not a Domain bundle",
                exit_code=EXIT_USAGE,
            )
        workspace = find_workspace(domain_file.resolve().parent) or find_project_root(domain_file)
        return review.Source(tree, workspace, _manifest(tree))

    tags = []
    domain_bundle = (
        domain_repo / "domain" / "bundles" / "domain-bundle.yaml" if domain_repo else None
    )
    if repo is not None and domain_bundle is not None and domain_bundle.is_file():
        data = yaml.safe_load(domain_bundle.read_text(encoding="utf-8")) or {}
        name = bundle_name(str(data.get("id", "")), domain_bundle)
        tags = sorted(
            (t for t in repo.version_tags() if t.workspace == "domain" and t.name == name),
            key=lambda t: split_version(t.version),
        )
    if domain_version is not None:
        tags = [t for t in tags if t.version == domain_version]
        if not tags:
            raise CommandError(
                "VERSION_NOT_FOUND", f"The Domain has no released version {domain_version}"
            )
    if not tags or repo is None:
        envelope.warning(
            "VIEW_DOMAIN_UNAVAILABLE",
            "No released Domain version was found, so the rules this Project inherits are not "
            "shown; pass --domain <file> to show a working Domain bundle",
        )
        return None
    checked = ValidationResult("versions")
    tagged = verify_tag(repo, tags[-1], checked)
    if tagged is None or tagged.tree is None:
        envelope.diagnostics.extend(diagnostics_from_results([checked]))
        return None
    return review.Source(tagged.tree, tagged.root, tagged.manifest, tags[-1].tag)
