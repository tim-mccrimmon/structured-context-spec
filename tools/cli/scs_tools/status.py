"""`scs status`: where a workspace stands, worked out from the repository (D-83).

Nothing here is stored: the status is read from the files, the intake record, and git each
time, so it cannot drift from them. A resumed or update session starts from it (D-85).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from scs_validator.envelope import relative
from scs_validator.gitrepo import GitRepo, GitUnavailable, split_version
from scs_validator.intake import INTAKE_FILE, load
from scs_validator.names import bundle_name, version_tag
from scs_validator.workspace import CONFIG, read_config

from scs_tools import git
from scs_tools.maintain import ROOT_BUNDLE_FILES

ENGINE_FIELDS = ("intake_version", "scs_version")
DECISIONS = ("changed", "kept", "deferred")
# Template placeholders: TODO markers (cdmo, mca) and bracketed hints such as "[Key need]" (sdlc)
PLACEHOLDER_RE = re.compile(r"\bTODO\b|[\"']\[[^\]\n]+\][\"']")


def workspaces(repo: Path) -> List[Path]:
    """The Domain workspace, then each Project workspace, of a Domain repository."""
    found = [repo / "domain"] if (repo / "domain" / CONFIG).is_file() else []
    projects = repo / "projects"
    if projects.is_dir():
        found += sorted(p for p in projects.iterdir() if (p / CONFIG).is_file())
    return found


def _yaml(path: Path) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _root_bundle(workspace: Path) -> Dict[str, Any]:
    for name in ROOT_BUNDLE_FILES:
        path = workspace / "bundles" / name
        if path.is_file():
            return _yaml(path)
    return {}


def _intake(workspace: Path) -> Dict[str, Any]:
    path = workspace / INTAKE_FILE
    if not path.is_file():
        return {"present": False}
    try:
        data = load(path) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    findings = [f for f in data.get("review_findings") or [] if isinstance(f, dict)]
    return {
        "present": True,
        "fields": sorted(k for k in data if k not in ENGINE_FIELDS),
        "answers": len(data.get("answers") or []),
        "approvers": [a.get("person") for a in data.get("approvers") or [] if isinstance(a, dict)],
        "source_documents": [
            d.get("id") for d in data.get("source_documents") or [] if isinstance(d, dict)
        ],
        "findings": {d: sum(1 for f in findings if f.get("decision") == d) for d in DECISIONS},
        "deferred": [f.get("id") for f in findings if f.get("decision") == "deferred"],
        "_documents": [d for d in data.get("source_documents") or [] if isinstance(d, dict)],
    }


def _sources(workspace: Path, documents: List[Dict[str, Any]], root: Path) -> Dict[str, Any]:
    """Files in sources/ that no source_documents entry names, and entries whose path is
    missing. A document may live in another workspace's sources/ (D-86)."""
    folder = workspace / "sources"
    files = (
        sorted(p for p in folder.rglob("*") if p.is_file() and p.name != "README.md")
        if folder.is_dir()
        else []
    )
    recorded = {(workspace / d["path"]).resolve(): d.get("id") for d in documents if d.get("path")}
    return {
        "files": [relative(p, root) for p in files],
        "unrecorded": [relative(p, root) for p in files if p.resolve() not in recorded],
        "missing": sorted(i for p, i in recorded.items() if i and not p.is_file()),
    }


def _scds(workspace: Path) -> Dict[str, Any]:
    paths = sorted((workspace / "context" / "project").glob("*.yaml"))
    placeholders = []
    for path in paths:
        try:
            if PLACEHOLDER_RE.search(path.read_text(encoding="utf-8")):
                placeholders.append(path.stem)
        except (OSError, UnicodeDecodeError):
            continue
    return {"count": len(paths), "placeholders": placeholders}


def _versions(repo: Optional[GitRepo], workspace: str, bundle_id: str) -> List[str]:
    if repo is None:
        return []
    name = bundle_name(bundle_id)
    try:
        tags = [t for t in repo.version_tags() if t.workspace == workspace and t.name == name]
    except GitUnavailable:
        return []
    return [t.version for t in sorted(tags, key=lambda t: split_version(t.version))]


def _changed_since(top: Path, tag: str, pathspec: str, pending: List[Dict[str, str]]) -> int:
    try:
        out = git.run(top, "diff", "--name-only", tag, "--", pathspec)
    except git.GitError:
        return 0
    return len({line for line in out.splitlines() if line} | {p["path"] for p in pending})


def workspace_status(
    path: Path, root: Path, repo: Optional[GitRepo], domain_versions: Optional[List[str]]
) -> Dict[str, Any]:
    try:
        config = read_config(path / CONFIG)
    except ValueError:
        config = {}
    name = "domain" if path == root / "domain" else path.name
    bundle = _root_bundle(path)
    bundle_id = str(bundle.get("id", f"bundle:{name}"))
    intake = _intake(path)
    documents = intake.pop("_documents", [])
    versions = _versions(repo, name, bundle_id)
    latest = versions[-1] if versions else None

    pending: List[Dict[str, str]] = []
    changed = None
    if repo is not None:
        pathspec = relative(path, repo.toplevel)
        try:
            pending = git.pending_paths(repo.toplevel, [pathspec])
        except git.GitError:
            pending = []
        if latest:
            tag = version_tag(name, bundle_name(bundle_id), latest)
            changed = _changed_since(repo.toplevel, tag, pathspec, pending)

    dist = path / "dist"
    artifacts = sorted(p.name for p in dist.glob("*") if p.is_file()) if dist.is_dir() else []
    stem = bundle_name(bundle_id)
    status: Dict[str, Any] = {
        "workspace": name,
        "path": relative(path, root),
        "kind": config.get("bundle_type"),
        "ontology": config.get("ontology") or config.get("ontology_model"),
        "bundle": bundle_id,
        "working_version": str(bundle.get("version", "")),
        "intake": intake,
        "sources": _sources(path, documents, root),
        "scds": _scds(path),
        "versions": versions,
        "latest_version": latest,
        "changed_since_version": changed,
        "uncommitted": (
            [
                {"path": relative(repo.toplevel / p["path"], root), "status": p["status"]}
                for p in pending
            ]
            if repo is not None
            else []
        ),
        "compiled": {
            "artifacts": artifacts,
            "latest_version_compiled": bool(latest)
            and any(a.startswith(f"{stem}-{latest}.") for a in artifacts),
        },
    }
    if name != "domain" and domain_versions is not None:
        status["domain_latest_version"] = domain_versions[-1] if domain_versions else None
    return status


def repository_status(root: Path, selected: List[Path]) -> Dict[str, Any]:
    """The status of each selected workspace in the repository at `root`."""
    repo: Optional[GitRepo] = None
    if git.available():
        try:
            repo = GitRepo.find(root)
        except GitUnavailable:
            repo = None
    domain_versions = None
    domain = root / "domain"
    if (domain / CONFIG).is_file():
        domain_versions = _versions(repo, "domain", str(_root_bundle(domain).get("id", "")))
    try:
        return {
            "repository": str(root),
            "workspaces": [workspace_status(p, root, repo, domain_versions) for p in selected],
        }
    finally:
        if repo is not None:
            repo.close()
