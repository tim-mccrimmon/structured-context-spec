"""`scs bundle release`: release a root bundle and the concept bundles it needs, in one command
(ISS-058).

A release is the cascade a root needs before it can be versioned: each changed concept bundle is
versioned and pinned in the root, bottom-up, then the root is versioned. Each step is the same
`scs bundle version` or `scs bundle pin` it would be on its own, with the same checks.

The dry run performs the whole cascade on a scratch copy of the repository, so it reports every
snapshot, manifest, pin, commit, and tag, the root's included, and the real run's changes match
it. On failure, the real run undoes every step it completed: HEAD, tags, index, and files are left
as they were (D-09).
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scs_validator.gitrepo import GitRepo, GitUnavailable, split_version
from scs_validator.names import bundle_name, manifest_name, snapshot_name, version_tag
from scs_validator.resolver import parse_bundle_ref, resolve

from scs_tools import git, maintain
from scs_tools.machine import EXIT_USAGE, CommandError, Envelope, Output
from scs_tools.versioning import VERSION_RE, _approver, _git_top, version_bundle
from scs_tools.workspace import workspace_name


@dataclass
class Step:
    """One concept bundle to release: its working file, the import it replaces, its version."""

    name: str
    bundle_id: str
    path: Path
    current: str
    version: str


def _parse_concepts(given: Tuple[str, ...]) -> Dict[str, str]:
    versions: Dict[str, str] = {}
    for item in given:
        name, sep, version = item.partition("=")
        name = bundle_name(name if name.startswith("bundle:") else f"bundle:{name}")
        if not sep or not name or not VERSION_RE.match(version):
            raise CommandError(
                "USAGE_ERROR",
                f"--concept takes NAME=VERSION, such as security=1.0.0; got '{item}'",
                exit_code=EXIT_USAGE,
            )
        versions[name] = version
    return versions


def _released(repo: Optional[GitRepo], workspace: str, name: str) -> List[str]:
    if repo is None:
        return []
    try:
        tags = [t for t in repo.version_tags() if t.workspace == workspace and t.name == name]
    except GitUnavailable:
        return []
    return [t.version for t in sorted(tags, key=lambda t: split_version(t.version))]


def _changed(top: Path, tag: str, path: Path) -> bool:
    """Whether the concept bundle or an SCD it lists differs from its released version."""
    tree = resolve(path)
    inputs = [path] + [s.path for s in tree.scds if s.bundle_id == tree.root.id]
    spec = [p.resolve().relative_to(top).as_posix() for p in inputs if p.is_file()]
    if not git.tag_exists(top, tag):
        return False  # the root's own version reports an untagged pin
    if git.run(top, "diff", "--name-only", tag, "--", *spec).strip():
        return True
    return bool(git.pending_paths(top, spec))


def plan(
    ws: maintain.Workspace, root_path: Path, root_data: Dict[str, Any], given: Dict[str, str]
) -> List[Step]:
    """The concept bundles this release versions, in the root's import order."""
    top = _git_top(ws.path)
    workspace = workspace_name(ws.path)
    local = {bundle_id: path for bundle_id, path, _ in ws.working_bundles() if path != root_path}
    repo = GitRepo.find(ws.path)
    steps: List[Step] = []
    missing: List[Dict[str, Any]] = []
    imported = set()
    for ref in [str(i) for i in root_data.get("imports") or []]:
        parsed = parse_bundle_ref(ref)
        if not parsed or parsed[0] not in local:
            continue  # not a concept bundle in this workspace, such as bundle:meta:<version>
        bundle_id, pinned = parsed
        name = bundle_name(bundle_id)
        imported.add(name)
        if name in given:
            reason = "requested"
        elif pinned is None:
            reason = "not pinned"
        elif _changed(top, version_tag(workspace, name, pinned), local[bundle_id]):
            reason = f"changed since {pinned}"
        else:
            continue
        if name not in given:
            released = _released(repo, workspace, name)
            missing.append(
                {
                    "concept": name,
                    "bundle": bundle_id,
                    "latest_version": released[-1] if released else None,
                    "reason": reason,
                }
            )
            continue
        steps.append(Step(name, bundle_id, local[bundle_id], ref, given[name]))
    unknown = sorted(set(given) - imported)
    if unknown:
        raise CommandError(
            "USAGE_ERROR",
            f"{root_data.get('id')} does not import a concept bundle in this workspace named "
            + ", ".join(unknown),
            exit_code=EXIT_USAGE,
        )
    if missing:
        listed = "; ".join(f"{m['concept']} ({m['reason']})" for m in missing)
        raise CommandError(
            "RELEASE_VERSION_REQUIRED",
            f"These concept bundles need a version in this release: {listed}. Pass one for each "
            "with --concept NAME=VERSION",
            exit_code=EXIT_USAGE,
            suggestion={"concepts": missing},
        )
    return steps


def _run(
    envelope: Envelope,
    root_path: Path,
    steps: List[Step],
    version: str,
    approver: str,
    notes: Optional[str],
    no_validate: bool,
    dry_run: bool,
) -> List[Dict[str, Any]]:
    """Version and pin each concept, then version the root. Stops at the first step that
    fails; returns what each completed step reported."""
    quiet = Output(True)
    done: List[Dict[str, Any]] = []
    for step in steps:
        version_bundle(
            envelope, quiet, step.path, step.version, approver, notes, no_validate, dry_run
        )
        if envelope.has_errors() or not (envelope.result or {}).get("tag"):
            return done
        done.append({"step": "version", **(envelope.result or {})})
        ws = maintain.open_workspace(None, root_path)
        maintain.pin(envelope, ws, root_path, step.bundle_id, step.version, dry_run)
        done.append({"step": "pin", **(envelope.result or {})})
    version_bundle(envelope, quiet, root_path, version, approver, notes, no_validate, dry_run)
    if not envelope.has_errors() and (envelope.result or {}).get("tag"):
        done.append({"step": "version", **(envelope.result or {})})
    return done


def _rehome(path: Path, top: Path, copy: Path) -> Path:
    return copy / path.resolve().relative_to(top)


def _dry_run(
    envelope: Envelope,
    top: Path,
    root_path: Path,
    steps: List[Step],
    version: str,
    approver: str,
    notes: Optional[str],
    no_validate: bool,
) -> List[Dict[str, Any]]:
    """The whole cascade, performed on a scratch copy of the repository."""
    if not (top / ".git").is_dir():
        # A linked worktree or submodule keeps its git directory elsewhere; a copy would share it.
        raise CommandError(
            "RELEASE_DRY_RUN_UNSUPPORTED",
            f"{top} keeps its git directory elsewhere (a linked worktree or submodule), so the "
            "release cannot be rehearsed on a copy; release from a standalone clone",
        )
    with tempfile.TemporaryDirectory(prefix="scs-release-") as scratch:
        copy = Path(scratch) / top.name
        shutil.copytree(top, copy, symlinks=True)
        moved = [
            Step(s.name, s.bundle_id, _rehome(s.path, top, copy), s.current, s.version)
            for s in steps
        ]
        done = _run(
            envelope,
            _rehome(root_path, top, copy),
            moved,
            version,
            approver,
            notes,
            no_validate,
            dry_run=False,
        )
    for change in envelope.changes:
        if change.action == "git-commit":
            change.ref = "HEAD"
    for entry in done:
        if entry.get("commit"):
            entry["commit"] = None
        entry["versioned"] = False if entry["step"] == "version" else entry.get("versioned")
        if entry["step"] == "pin":
            entry.pop("versioned", None)
    return done


def _undo(top: Path, old: Optional[str], saved_index: Optional[bytes], saved: Dict[Path, str],
          tags: List[str], written: List[Path]) -> None:  # fmt: skip
    """Put the repository back as it was before the release."""
    for tag in tags:
        if git.tag_exists(top, tag):
            git.run(top, "tag", "-d", tag)
    current = git.head(top)
    if old and current and current != old:
        git.move_head(top, old, current, "scs bundle release: roll back")
    index = git.index_file(top)
    if saved_index is None:
        index.unlink(missing_ok=True)
    else:
        index.write_bytes(saved_index)
    for path in written:
        path.unlink(missing_ok=True)
    for path, text in saved.items():
        path.write_text(text, encoding="utf-8")


def release_bundle(
    envelope: Envelope,
    out: Output,
    bundle_file: Optional[Path],
    workspace: Optional[str],
    version: str,
    concepts: Tuple[str, ...],
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
    given = _parse_concepts(concepts)
    ws = maintain.open_workspace(workspace, bundle_file)
    root_path = (bundle_file.resolve() if bundle_file is not None else ws.root_bundle()).resolve()
    root_path, root_data = maintain._target(ws, root_path)
    approver = _approver(approved_by)
    top = _git_top(ws.path)
    steps = plan(ws, root_path, root_data, given)

    if dry_run:
        try:
            done = _dry_run(envelope, top, root_path, steps, version, approver, notes, no_validate)
        except BaseException:
            envelope.changes.clear()
            raise
    else:
        old = git.head(top)
        index = git.index_file(top)
        saved_index = index.read_bytes() if index.is_file() else None
        saved = {root_path: root_path.read_text(encoding="utf-8")}
        workspace_label = workspace_name(ws.path)
        names = [(s.path, s.name, s.version) for s in steps]
        names.append((root_path, bundle_name(str(root_data.get("id", "")), root_path), version))
        tags = [version_tag(workspace_label, n, v) for _, n, v in names]
        tags = [tag for tag in tags if not git.tag_exists(top, tag)]  # only what this run makes
        written = [p.parent / f(n, v) for p, n, v in names for f in (snapshot_name, manifest_name)]
        written = [p for p in written if not p.exists()]
        try:
            done = _run(envelope, root_path, steps, version, approver, notes, no_validate, False)
        except BaseException:
            _undo(top, old, saved_index, saved, tags, written)
            envelope.changes.clear()
            raise
        if envelope.has_errors():
            _undo(top, old, saved_index, saved, tags, written)
            envelope.changes.clear()

    released = [d for d in done if d["step"] == "version"]
    complete = not envelope.has_errors() and len(released) == len(steps) + 1
    envelope.result = {
        "released": complete and not dry_run,
        "bundle": root_data.get("id"),
        "version": version,
        "steps": done if complete else [],
    }
    if not complete:
        envelope.changes.clear()
        out.echo("Release stopped; nothing was released.", err=True)
        return
    suffix = " (dry run, nothing written)" if dry_run else ""
    out.echo(f"Released {root_data.get('id')} {version}{suffix}")
    for entry in done:
        if entry["step"] == "version":
            out.echo(f"  Versioned {entry['bundle']} {entry['version']} as {entry['tag']}")
        else:
            out.echo(f"  Pinned {entry['import']} in {entry['bundle']}")
    if not dry_run:
        tags_text = " ".join(d["tag"] for d in released)
        out.echo(f"  Push it with: git push && git push origin {tags_text}")
