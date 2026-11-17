"""Integrity of versions: the git tag is the record of a version (D-39, plan section 5).

A version of a bundle is the tag `<workspace>/<bundle-name>-v<version>` on a commit holding the
whole workspace. Three checks follow:

1. Every version tag: the digest recomputed from the tagged content equals the tagged
   manifest's `content_digest`, and each pinned import's manifest at that commit equals the
   import's own tagged manifest.
2. Working copies of versions still in use (pinned by a working bundle, or the latest version
   of a bundle whose working file exists) equal their tagged copies by git blob id.
3. Drift: each pinned import of a working bundle matches its versioned content. The bundle
   validator runs this one against the working manifest, which check 2 ties to the tag.

Tags without the workspace qualifier predate 0.7 and are history: not verified, not reported
(D-54).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from .checks._shared import shown
from .digest import ContentDigest, DigestError, changes, content_digest, find_version_manifest
from .gitrepo import GitRepo, GitUnavailable, VersionTag, find_file, split_version, workspace_dir
from .names import bundle_name, is_snapshot, manifest_name, snapshot_name, version_tag
from .resolver import PACKAGED_META, BundleTree, Index, parse_bundle_ref, resolve
from .utils import ValidationError, ValidationResult
from .workspace import Workspace

MANIFEST_RE = re.compile(r"^(?P<name>.+)-v(?P<version>\d+\.\d+\.\d+)-MANIFEST$")


@dataclass
class TaggedVersion:
    """A version read from its tag: the workspace as committed, written to a temporary
    directory, with the manifest and snapshot found there."""

    tag: VersionTag
    root: Path  # the workspace directory at the tag
    workspace_path: str  # the workspace's path from the git top level
    manifest_path: Path
    manifest: Dict[str, Any]
    snapshot_path: Path
    tree: Optional[BundleTree] = None
    digest: Optional[ContentDigest] = None
    index: Optional[Index] = None

    def repo_path(self, path: Path) -> str:
        """A file of the checkout as its path from the git top level."""
        return str(PurePosixPath(self.workspace_path, path.relative_to(self.root).as_posix()))


@dataclass
class Integrity:
    """The results of the checks, and the tags they read."""

    result: ValidationResult = field(default_factory=lambda: ValidationResult("versions"))
    verified: Dict[str, TaggedVersion] = field(default_factory=dict)


def _error(result: ValidationResult, code: str, message: str, path: Optional[str]) -> None:
    result.add_error(ValidationError(message, file_path=path, code=code))


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError):
        return None


def _in_workspace(bundle_path: Path, root: Path) -> bool:
    try:
        bundle_path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_tag(git: GitRepo, tag: VersionTag, result: ValidationResult) -> Optional[TaggedVersion]:
    """The version at `tag`, or None (with the error in `result`) when the tagged commit holds no
    usable manifest or snapshot."""
    workspace_path = git.path(workspace_dir(tag.workspace))
    root = git.checkout(tag.commit, workspace_path)
    manifest_path = find_file(root, manifest_name(tag.name, tag.version))
    if manifest_path is None:
        _error(
            result,
            "VERSION_MANIFEST_MISSING",
            f"Tag {tag.tag} points at a commit without {manifest_name(tag.name, tag.version)} in "
            f"{workspace_path}/bundles; a version tag must point at its own version commit",
            tag.tag,
        )
        return None
    manifest = _load_yaml(manifest_path)
    if not isinstance(manifest, dict):
        _error(
            result,
            "VERSION_MANIFEST_MISSING",
            f"Tag {tag.tag}: the version manifest cannot be read",
            tag.tag,
        )
        return None
    file_name = str((manifest.get("bundle") or {}).get("file") or "")
    snapshot_path = manifest_path.parent / (file_name or snapshot_name(tag.name, tag.version))
    tagged = TaggedVersion(
        tag, root, workspace_path, manifest_path, manifest, snapshot_path, index=None
    )
    missing = [key for key in ("content_digest", "tools_version") if not manifest.get(key)]
    if missing:
        _error(
            result,
            "VERSION_MANIFEST_INCOMPLETE",
            f"Tag {tag.tag}: the manifest has no {' or '.join(missing)}; a manifest with a "
            "workspace-qualified tag is an SCS 0.7 manifest and must carry both (D-49)",
            tagged.repo_path(manifest_path),
        )
        return None
    if not snapshot_path.is_file():
        _error(
            result,
            "CONTENT_DIGEST_MISMATCH",
            f"Tag {tag.tag}: the snapshot {snapshot_path.name} is not in the tagged commit",
            tagged.repo_path(manifest_path),
        )
        return None
    return tagged


def verify_tag(git: GitRepo, tag: VersionTag, result: ValidationResult) -> Optional[TaggedVersion]:
    """Check 1 for one tag. Returns the verified version, or None with errors in `result`."""
    tagged = read_tag(git, tag, result)
    if tagged is None:
        return None
    index = Index([PACKAGED_META, tagged.root])
    tree = resolve(tagged.snapshot_path, index=index)
    try:
        digest = content_digest(tree.root, index)
    except DigestError as e:
        _error(result, "CONTENT_DIGEST_MISMATCH", f"Tag {tag.tag}: {e}", tag.tag)
        return None
    tagged.tree, tagged.digest, tagged.index = tree, digest, index
    ok = True
    if digest.digest != tagged.manifest.get("content_digest"):
        changed = ", ".join(
            changes(digest, tagged.manifest.get("content_inputs"), tagged.repo_path)
        )
        _error(
            result,
            "CONTENT_DIGEST_MISMATCH",
            f"Tag {tag.tag}: the tagged content does not match the tagged manifest's "
            f"content_digest; changed: {changed or 'unknown'}. The tag was moved or the "
            "content was rewritten after it was versioned",
            tagged.repo_path(tagged.manifest_path),
        )
        ok = False
    for ref in tree.root.data.get("imports") or []:
        parsed = parse_bundle_ref(str(ref))
        if not parsed or parsed[1] is None:
            continue
        target, mismatch = index.find_bundle(str(ref))
        if target is None or mismatch or not _in_workspace(target.path, tagged.root):
            continue
        name, version = bundle_name(target.id), parsed[1]
        here = find_file(tagged.root, manifest_name(name, version))
        own_tag = version_tag(tag.workspace, name, version)
        own_commit = git.tag_commit(own_tag)
        if own_commit is None:
            _error(
                result,
                "VERSION_TAG_MISSING",
                f"Tag {tag.tag} pins {ref}, which has no tag {own_tag}",
                tagged.repo_path(tagged.snapshot_path),
            )
            ok = False
            continue
        own_root = git.checkout(own_commit, tagged.workspace_path)
        theirs = find_file(own_root, manifest_name(name, version))
        here_blob = git.blob_at(tag.commit, tagged.repo_path(here)) if here else None
        their_blob = (
            git.blob_at(
                own_commit,
                str(PurePosixPath(tagged.workspace_path, theirs.relative_to(own_root).as_posix())),
            )
            if theirs
            else None
        )
        if here_blob is None or here_blob != their_blob:
            _error(
                result,
                "CONTENT_DIGEST_MISMATCH",
                f"Tag {tag.tag} pins {ref}, but the manifest of {ref} in its commit differs from "
                f"the one at {own_tag}",
                tagged.repo_path(here) if here else tag.tag,
            )
            ok = False
    return tagged if ok else None


def _working_bundles(root: Path) -> List[Tuple[Path, Dict[str, Any]]]:
    """Working bundle files of a workspace (not snapshots), with their data."""
    found: List[Tuple[Path, Dict[str, Any]]] = []
    bundles = root / "bundles"
    if not bundles.is_dir():
        return found
    for path in sorted(bundles.rglob("*.yaml")):
        if is_snapshot(path) or path.stem.endswith("-MANIFEST"):
            continue
        data = _load_yaml(path)
        if isinstance(data, dict) and str(data.get("id", "")).startswith("bundle:"):
            found.append((path, data))
    return found


def _check_working_copies(
    git: Optional[GitRepo], workspace: Workspace, tags: List[VersionTag], result: ValidationResult
) -> None:
    """Check 2, and a 0.7 manifest with no tag (VERSION_TAG_MISSING), for one workspace."""
    mine = {(t.name, t.version): t for t in tags if t.workspace == workspace.name}
    working = _working_bundles(workspace.root)
    names = {bundle_name(str(data["id"])) for _, data in working}
    in_use: Set[Tuple[str, str]] = set()
    for _, data in working:
        for ref in data.get("imports") or []:
            parsed = parse_bundle_ref(str(ref))
            if parsed and parsed[1] is not None:
                in_use.add((bundle_name(parsed[0]), parsed[1]))
    for name in names:
        versions = [v for n, v in mine if n == name]
        if versions:
            in_use.add((name, max(versions, key=split_version)))

    if git is not None:
        workspace_path = workspace.root.resolve().relative_to(git.toplevel).as_posix()
        for name, version in sorted(in_use):
            tag = mine.get((name, version))
            if tag is None:
                continue
            files = git.files(tag.commit, workspace_path)
            wanted = {manifest_name(name, version), snapshot_name(name, version)}
            for repo_path, blob in sorted(files.items()):
                if PurePosixPath(repo_path).name not in wanted:
                    continue
                if "/bundles/" not in f"/{repo_path}":
                    continue
                current = git.working_blob(repo_path)
                if current == blob:
                    continue
                what = "has been deleted" if current is None else "differs from its tagged copy"
                _error(
                    result,
                    "MANIFEST_ALTERED",
                    f"{repo_path} {what} ({tag.tag}). A released version's manifest and snapshot "
                    f"are not edited; restore it with: git checkout {tag.tag} -- {repo_path}",
                    shown(git.toplevel / repo_path),
                )

    bundles = workspace.root / "bundles"
    for path in sorted(bundles.rglob("*-MANIFEST.yaml")) if bundles.is_dir() else []:
        match = MANIFEST_RE.match(path.stem)
        if path.name.startswith("VERSION-") or not match:
            continue
        data = _load_yaml(path)
        if not isinstance(data, dict) or not data.get("content_digest"):
            continue
        name, version = match.group("name"), match.group("version")
        if (name, version) not in mine:
            expected = version_tag(workspace.name, name, version)
            _error(
                result,
                "VERSION_TAG_MISSING",
                f"{path.name} records a content digest but there is no tag {expected}; a version "
                "exists only as its tag. Restore the tag, or remove the manifest and snapshot if "
                "the version was never released",
                shown(path),
            )


def verify_repository(repo: Path, workspaces: List[Workspace]) -> ValidationResult:
    """Checks 1 and 2 over a Domain repository (repository mode)."""
    result = ValidationResult("versions")
    try:
        git = GitRepo.find(repo)
    except GitUnavailable as e:
        _error(result, "GIT_REQUIRED", f"Version checks need git: {e}", str(repo))
        return result
    if git is None:
        for workspace in workspaces:
            _check_working_copies(None, workspace, [], result)
        return result
    with git:
        if git.is_shallow():
            _error(
                result,
                "GIT_HISTORY_INCOMPLETE",
                "This is a shallow clone, so version tags cannot be checked. Fetch full history "
                "and tags (git fetch --unshallow --tags; in GitHub Actions, fetch-depth: 0)",
                str(repo),
            )
            return result
        tags = git.version_tags()
        for tag in tags:
            verify_tag(git, tag, result)
        for workspace in workspaces:
            _check_working_copies(git, workspace, tags, result)
    return result


def verify_one(repo: Path, tag_name: str) -> Tuple[ValidationResult, Optional[TaggedVersion]]:
    """`--verify-version <tag>`: check 1 for a single tag."""
    result = ValidationResult("versions")
    git = GitRepo.find(repo)
    if git is None:
        _error(result, "GIT_REQUIRED", f"{repo} is not in a git repository", str(repo))
        return result, None
    with git:
        match = [t for t in git.version_tags() if t.tag == tag_name]
        if not match:
            _error(
                result,
                "VERSION_NOT_FOUND",
                f"No version tag {tag_name} (expected <workspace>/<bundle-name>-v<version>)",
                tag_name,
            )
            return result, None
        return result, verify_tag(git, match[0], result)


def check_pinned(
    tree: BundleTree,
    git: Optional[GitRepo],
    workspace: str,
    workspace_root: Path,
    require_tags: bool,
) -> ValidationResult:
    """Integrity of the versioned bundles a working tree pins (D-14, D-16, D-53): each matches
    its versioned content (drift), and, in a git repository, its working manifest and snapshot
    equal the tagged copies. With `require_tags`, a version without a 0.7 tag is refused.
    Bundles outside the workspace (the packaged meta bundle) are fixed by the tools version."""
    result = ValidationResult("versions")
    index = tree.index or Index([PACKAGED_META, tree.project_root])
    for bundle in tree.bundles[1:]:
        if not bundle.version or bundle.version == "DRAFT":
            continue
        if not _in_workspace(bundle.path, workspace_root):
            continue
        name, version = bundle_name(bundle.id), bundle.version
        found = find_version_manifest(bundle)
        recorded = found[1].get("content_digest") if found else None
        if not recorded:
            if require_tags:
                _error(
                    result,
                    "VERSION_TAG_MISSING",
                    f"{bundle.id}:{version} has no SCS 0.7 version (no content digest); version "
                    f"it under 0.7 first, then pin the new version",
                    shown(bundle.path),
                )
            continue
        try:
            actual = content_digest(bundle, index)
        except DigestError:
            continue
        if actual.digest != recorded:
            changed = ", ".join(changes(actual, found[1].get("content_inputs"))) if found else ""
            _error(
                result,
                "CONTENT_DIGEST_MISMATCH",
                f"{bundle.id}:{version} has changed since it was versioned; changed: "
                f"{changed or 'unknown'}. Version it again, then re-pin it",
                shown(bundle.path),
            )
        if git is None:
            continue
        tag = version_tag(workspace, name, version)
        commit = git.tag_commit(tag)
        if commit is None:
            _error(
                result,
                "VERSION_TAG_MISSING",
                f"{bundle.id}:{version} has a manifest with a content digest but no tag {tag}",
                shown(bundle.path),
            )
            continue
        workspace_path = workspace_root.resolve().relative_to(git.toplevel).as_posix()
        for path in (found[0] if found else None, bundle.path):
            if path is None:
                continue
            relative = path.resolve().relative_to(git.toplevel).as_posix()
            tagged = git.blob_at(commit, relative)
            if tagged is None:
                tagged_files = git.files(commit, workspace_path)
                tagged = next(
                    (b for p, b in tagged_files.items() if PurePosixPath(p).name == path.name),
                    None,
                )
            if tagged != git.working_blob(relative):
                _error(
                    result,
                    "MANIFEST_ALTERED",
                    f"{relative} differs from its copy at {tag}",
                    relative,
                )
    return result
