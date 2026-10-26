"""`scs bundle version`: release a bundle as a tagged version (plan section 5, D-39, D-40).

A version is the tag `<workspace>/<bundle-name>-v<version>` on a commit holding the whole
workspace except `dist/`. The run writes the snapshot and the version manifest beside the bundle,
commits the workspace with the approver as author and the engine as committer, and tags that
commit. Integrity checks always run; content validation runs unless `--no-validate` (D-53).
On failure, everything the run wrote is removed and HEAD is left where it was (D-09).
"""

from __future__ import annotations

import hashlib
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from scs_validator import api, integrity
from scs_validator.checks.empty_scds import is_empty
from scs_validator.digest import DigestError, content_digest
from scs_validator.envelope import Change, diagnostics_from_results, relative
from scs_validator.gitrepo import GitRepo, GitUnavailable
from scs_validator.names import bundle_name, manifest_name, snapshot_name, version_tag
from scs_validator.provenance import is_placeholder
from scs_validator.resolver import BundleTree, ResolvedBundle, parse_bundle_ref, resolve
from scs_validator.workspace import CONFIG, LEGACY_ONTOLOGY_MANIFEST, ONTOLOGY_MANIFEST

from scs_tools import __version__, git, identity
from scs_tools.machine import EXIT_USAGE, CommandError, Envelope, Output
from scs_tools.workspace import find_workspace, repository_root, workspace_name

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
# A person identifier, as the version manifest schema requires (D-28).
PERSON_RE = re.compile(r"^[^<>\s][^<>]*\s<[^<>\s@]+@[^<>\s@]+>$")


@dataclass
class Release:
    """Everything one run will write, worked out before anything is written."""

    bundle_path: Path
    workspace_root: Path
    workspace: str
    git_top: Path
    root: Path  # the repository root envelope paths are relative to (D-42)
    name: str
    version: str
    tag: str
    approver: str
    notes: str
    snapshot_path: Path
    manifest_path: Path
    snapshot_text: str = ""
    manifest_text: str = ""
    digest: str = ""
    empty_scds: List[str] = field(default_factory=list)

    def shown(self, path: Path) -> str:
        return relative(path, self.root)

    def from_top(self, path: Path) -> str:
        return path.resolve().relative_to(self.git_top).as_posix()

    @property
    def pathspec(self) -> List[str]:
        """The workspace except dist/ (D-40)."""
        top = self.from_top(self.workspace_root)
        if top in ("", "."):
            return [".", ":(exclude)dist"]
        return [top, f":(exclude){top}/dist"]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _approver(given: Optional[str]) -> str:
    """The approver, required in every mode and never taken from git (D-13). Git's identity
    appears only as the suggestion."""
    approver = (given or "").strip()
    if not approver:
        suggested = identity.person_suggestion()
        raise CommandError(
            "VERSION_APPROVER_REQUIRED",
            "A version needs an approver: pass --approved-by 'Name <email>'. It is never taken "
            "from git configuration",
            suggestion={"approved_by": suggested} if suggested else None,
        )
    if not PERSON_RE.match(approver) or approver.startswith("role:"):
        raise CommandError(
            "VERSION_APPROVER_INVALID",
            f"The approver must be a person identifier, Name <email>; got '{approver}'",
        )
    return approver


def _git_top(workspace_root: Path) -> Path:
    if not git.available():
        raise CommandError("GIT_REQUIRED", "Versioning needs git: a version is a git tag (D-38)")
    try:
        found = GitRepo.find(workspace_root)
    except GitUnavailable as e:
        raise CommandError("GIT_REQUIRED", f"Versioning needs git: {e}")
    if found is None:
        raise CommandError(
            "GIT_REQUIRED",
            f"{workspace_root} is not in a git repository; a version is a git tag (D-38)",
        )
    return found.toplevel


def _check_imports(tree: BundleTree, envelope: Envelope, release: Release) -> None:
    """Every import is pinned to a released version (D-14), whatever --no-validate says."""
    index = tree.index
    assert index is not None
    for ref in tree.root.data.get("imports") or []:
        ref = str(ref)
        parsed = parse_bundle_ref(ref)
        target, mismatch = index.find_bundle(ref)
        problem = None
        if not parsed or parsed[1] is None:
            problem = "is not pinned; pin it to a released version (bundle:<name>:<version>)"
        elif target is None or mismatch:
            problem = "does not resolve to a released version"
        elif target.version == "DRAFT":
            problem = "is at DRAFT; version it first, then pin it"
        if problem:
            envelope.error(
                "VERSION_IMPORT_NOT_PINNED",
                f"Import {ref} {problem}",
                release.shown(release.bundle_path),
            )


def _check_placeholders(tree: BundleTree, envelope: Envelope, release: Release) -> None:
    """No placeholder created_by in the bundle or the SCDs it lists (D-71)."""
    documents = [(tree.root.id, tree.root.path, tree.root.data)]
    documents += [(s.ref, s.path, s.data) for s in tree.scds if s.bundle_id == tree.root.id]
    for doc_id, path, data in documents:
        provenance = data.get("provenance")
        created_by = provenance.get("created_by") if isinstance(provenance, dict) else None
        if is_placeholder(created_by):
            envelope.error(
                "VERSION_PROVENANCE_PLACEHOLDER",
                f"{doc_id} has the placeholder created_by '{created_by}'; set it to who created "
                "it before versioning",
                release.shown(path),
            )


def _inputs(tree: BundleTree, release: Release) -> List[Path]:
    """Files the digest and the compiler read, inside the workspace (D-40)."""
    paths = [b.path for b in tree.bundles] + [s.path for s in tree.scds]
    for extra in (CONFIG, ONTOLOGY_MANIFEST, LEGACY_ONTOLOGY_MANIFEST, Path("intake.yaml")):
        paths.append(release.workspace_root / extra)
    inside = []
    for path in paths:
        try:
            path.resolve().relative_to(release.workspace_root.resolve())
        except ValueError:
            continue
        if path.is_file():
            inside.append(path)
    return inside


def _snapshot(data: Dict[str, Any], release: Release, validated: bool) -> str:
    snapshot = dict(data)
    # The snapshot is the released bundle: it carries the released version, which the approval
    # fields attest to and `bundle:<name>:<version>` imports pin. The working file stays DRAFT.
    snapshot["version"] = release.version
    provenance = dict(snapshot.get("provenance") or {})
    timestamp = _now()
    provenance["version_approved_by"] = release.approver
    provenance["version_approved_at"] = timestamp
    provenance["approval_status"] = "validated" if validated else "approved"
    provenance["validation_passed"] = validated
    if validated:
        provenance["validation_date"] = timestamp
    provenance["version_notes"] = release.notes
    snapshot["provenance"] = provenance
    return str(yaml.dump(snapshot, default_flow_style=False, sort_keys=False, allow_unicode=True))


def _manifest(
    release: Release,
    data: Dict[str, Any],
    content_inputs: Dict[str, Any],
    validation: Optional[Dict[str, Any]],
    branch: Optional[str],
) -> str:
    snapshot_bytes = release.snapshot_text.encode("utf-8")
    imports = [str(i) for i in data.get("imports") or []]
    meta = [i for i in imports if i.split(":")[1:2] == ["meta"]]
    timestamp = _now()
    manifest: Dict[str, Any] = {
        "version": release.version,
        "release_date": timestamp,
        "status": "validated" if validation else "approved",
        "project": release.name,
        "tools_version": __version__,
        "bundle": {
            "id": data.get("id"),
            "type": data.get("type"),
            "file": release.snapshot_path.name,
            "sha256": hashlib.sha256(snapshot_bytes).hexdigest(),
            "size_bytes": len(snapshot_bytes),
        },
        "content_digest": release.digest,
        "content_inputs": content_inputs,
    }
    if validation:
        manifest["validation"] = {"validation_date": timestamp, **validation}
    manifest["components"] = {
        "meta_bundles": meta,
        "imported_bundles": [i for i in imports if i not in meta],
        "total_scds": len(data.get("scds") or []),
    }
    manifest["approval"] = {
        "approved_by": release.approver,
        "approved_at": timestamp,
        "approval_notes": release.notes,
    }
    manifest["release_notes"] = release.notes
    distribution: Dict[str, Any] = {"repository": release.git_top.name}
    if branch:
        distribution["branch"] = branch
    distribution.update({"tag": release.tag, "immutable": True, "authoritative": True})
    manifest["distribution"] = distribution
    return str(yaml.dump(manifest, default_flow_style=False, sort_keys=False, allow_unicode=True))


def _branch(top: Path) -> Optional[str]:
    try:
        return git.run(top, "symbolic-ref", "--short", "-q", "HEAD").strip() or None
    except git.GitError:
        return None


def _validate(release: Release, envelope: Envelope) -> Dict[str, Any]:
    try:
        report = api.validate_bundle(release.bundle_path)
    except api.SchemaDirNotFound:
        raise CommandError("SCHEMA_DIR_NOT_FOUND", "Schema directory not found; set SCS_SCHEMA_DIR")
    results = report.all_results()
    if report.exit_code() == 1:
        envelope.diagnostics.extend(
            d for d in diagnostics_from_results(results) if d.severity == "error"
        )
    return {
        "validator_version": __version__,
        "passed": report.exit_code() != 1,
        "errors": sum(r.error_count for r in results),
        "warnings": sum(r.warning_count for r in results),
    }


def _commit(release: Release, envelope: Envelope, dry_run: bool) -> Optional[str]:
    """Commit the workspace and tag the commit; on failure, undo everything this run wrote."""
    top = release.git_top
    message = (
        f"Version {release.name} {release.version}\n\n{release.notes}\n\n"
        f"Approved-by: {release.approver}\nContent-digest: {release.digest}\n"
    )
    if dry_run:
        pending = git.pending_paths(top, release.pathspec)
        written = {release.from_top(release.snapshot_path), release.from_top(release.manifest_path)}
        paths = [p for p in pending if p["path"] not in written]
        paths += [{"path": p, "status": "A"} for p in sorted(written)]
        paths.sort(key=lambda p: p["path"])
        envelope.changes.append(Change("git-commit", ref="HEAD", paths=_from_root(paths, release)))
        envelope.changes.append(Change("git-tag", ref=release.tag))
        return None

    old = git.head(top)
    index = git.index_file(top)
    saved_index = index.read_bytes() if index.is_file() else None
    commit = ""
    tagged = moved = False
    try:
        release.snapshot_path.write_text(release.snapshot_text, encoding="utf-8")
        release.manifest_path.write_text(release.manifest_text, encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="scs-version-") as work:
            commit = git.commit_paths(top, release.pathspec, message, release.approver, Path(work))
        git.run(top, "tag", "-a", release.tag, commit, "-m", _tag_message(release))
        tagged = True
        git.move_head(top, commit, old, f"scs bundle version {release.tag}")
        moved = True
        git.sync_index(top, release.pathspec)
    except BaseException as e:
        _roll_back(release, old, commit if moved else None, tagged)
        if saved_index is None:
            index.unlink(missing_ok=True)
        else:
            index.write_bytes(saved_index)
        envelope.changes.clear()
        if isinstance(e, (git.GitError, OSError)):
            raise CommandError("GIT_COMMAND_FAILED", f"{e}; nothing was versioned")
        raise
    envelope.changes.append(
        Change(
            "git-commit", ref=commit, paths=_from_root(git.committed_paths(top, commit), release)
        )
    )
    envelope.changes.append(Change("git-tag", ref=release.tag))
    return commit


def _roll_back(release: Release, old: Optional[str], moved_to: Optional[str], tagged: bool) -> None:
    """Undo a failed run: HEAD back where it was, no tag, no snapshot or manifest (D-09)."""
    top = release.git_top
    try:
        if moved_to and old:
            git.move_head(top, old, moved_to, "scs bundle version: roll back")
        elif moved_to:
            git.run(top, "update-ref", "-d", "HEAD", moved_to)
        if tagged:
            git.run(top, "tag", "-d", release.tag)
    finally:
        for path in (release.snapshot_path, release.manifest_path):
            path.unlink(missing_ok=True)


def _from_root(paths: List[Dict[str, str]], release: Release) -> List[Dict[str, str]]:
    """Paths from the git top level as paths from the repository root (D-42)."""
    return [
        {"path": relative(release.git_top / p["path"], release.root), "status": p["status"]}
        for p in paths
    ]


def _tag_message(release: Release) -> str:
    return (
        f"{release.name} {release.version}\n\n"
        f"Approved by: {release.approver}\nContent digest: {release.digest}\n"
    )


def version_bundle(
    envelope: Envelope,
    out: Output,
    bundle_path: Path,
    version: str,
    approved_by: Optional[str],
    notes: Optional[str],
    no_validate: bool,
    dry_run: bool,
) -> None:
    if not VERSION_RE.match(version):
        raise CommandError(
            "VERSION_INVALID",
            f"Invalid version '{version}': use MAJOR.MINOR.PATCH, such as 1.0.0",
            exit_code=EXIT_USAGE,
        )
    if not bundle_path.is_file():
        raise CommandError("FILE_NOT_FOUND", f"No such bundle file: {bundle_path}", exit_code=4)
    bundle_path = bundle_path.resolve()
    workspace_root = find_workspace(bundle_path.parent) or bundle_path.parent.parent
    top = _git_top(workspace_root)
    approver = _approver(approved_by)

    data = yaml.safe_load(bundle_path.read_text(encoding="utf-8")) or {}
    name = bundle_name(str(data.get("id", "")), bundle_path)
    workspace = workspace_name(workspace_root)
    release = Release(
        bundle_path=bundle_path,
        workspace_root=workspace_root,
        workspace=workspace,
        git_top=top,
        root=repository_root(workspace_root) or top,
        name=name,
        version=version,
        tag=version_tag(workspace, name, version),
        approver=approver,
        notes=notes or f"Version {version}",
        snapshot_path=bundle_path.parent / snapshot_name(name, version),
        manifest_path=bundle_path.parent / manifest_name(name, version),
    )

    if git.tag_exists(top, release.tag) or any(
        p.exists() for p in (release.snapshot_path, release.manifest_path)
    ):
        raise CommandError(
            "VERSION_EXISTS",
            f"{data.get('id')} {version} already exists ({release.tag}); a released version is "
            "never overwritten. Choose a new version",
            path=release.shown(release.snapshot_path),
        )

    # Integrity checks always run (D-53): pinned imports, their tags, placeholder provenance.
    tree = resolve(bundle_path)
    _check_imports(tree, envelope, release)
    repo = GitRepo.find(workspace_root)
    assert repo is not None
    with repo:
        pinned = integrity.check_pinned(tree, repo, workspace, workspace_root, require_tags=True)
    envelope.diagnostics.extend(diagnostics_from_results([pinned]))
    _check_placeholders(tree, envelope, release)
    ignored = git.ignored(top, [release.from_top(p) for p in _inputs(tree, release)])
    for path in ignored:
        envelope.error(
            "VERSION_INPUT_UNTRACKED",
            f"{path} is read by the digest or the compiler but git ignores it, so the version "
            "commit would not hold it; stop ignoring it",
            relative(top / path, release.root),
        )
    if envelope.has_errors():
        envelope.result = {"versioned": False}
        return

    validation = None
    if not no_validate:
        validation = _validate(release, envelope)
        if not validation["passed"]:
            envelope.result = {"versioned": False}
            out.echo("Validation failed; fix the errors or version with --no-validate.", err=True)
            return

    release.empty_scds = sorted(
        s.ref for s in tree.scds if s.bundle_id == tree.root.id and is_empty(s.data)
    )
    for ref in release.empty_scds:
        envelope.info(
            "SCD_EMPTY",
            f"{ref} has no prohibitions, directives, or facts; it is versioned but contributes "
            "nothing. Remove it first if it is not needed",
        )

    release.snapshot_text = _snapshot(data, release, validated=validation is not None)
    snapshot_data = yaml.safe_load(release.snapshot_text)
    snapshot = ResolvedBundle(
        id=str(snapshot_data.get("id")),
        type=snapshot_data.get("type"),
        version=version,
        data=snapshot_data,
        path=release.snapshot_path,
    )
    assert tree.index is not None
    try:
        digest = content_digest(snapshot, tree.index)
    except DigestError as e:
        raise CommandError("VERSION_IMPORT_NOT_PINNED", str(e))
    release.digest = digest.digest
    content_inputs, _ = digest.inputs()
    release.manifest_text = _manifest(release, data, content_inputs, validation, _branch(top))

    for written in (release.snapshot_path, release.manifest_path):
        envelope.changes.append(Change("create", path=release.shown(written)))
    commit = _commit(release, envelope, dry_run)
    envelope.result = {
        "versioned": not dry_run,
        "bundle": data.get("id"),
        "version": version,
        "tag": release.tag,
        "commit": commit,
        "snapshot": release.shown(release.snapshot_path),
        "manifest": release.shown(release.manifest_path),
        "content_digest": release.digest,
        "validated": validation is not None,
        "empty_scds": release.empty_scds,
    }
    suffix = " (dry run, nothing written)" if dry_run else ""
    out.echo(f"Versioned {data.get('id')} {version} as {release.tag}{suffix}")
    out.echo(f"  Snapshot:       {release.shown(release.snapshot_path)}")
    out.echo(f"  Manifest:       {release.shown(release.manifest_path)}")
    out.echo(f"  Content digest: {release.digest}")
    if not dry_run:
        out.echo(f"  Push it with:   git push && git push origin {release.tag}")
