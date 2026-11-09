"""`scs bundle release`: the version cascade in one command (ISS-058)."""

# ruff: noqa: F811  (the repo fixture comes from test_maintain)

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List

import yaml
from test_maintain import (  # noqa: F401
    APPROVER,
    app,
    codes,
    envelope,
    files,
    fill,
    git_state,
    repo,
    run,
)


def _concepts(repo: Path) -> List[Dict]:
    data = envelope(run("bundle", "release", "-v", "1.0.0", "--approved-by", APPROVER, "--json"))
    assert codes(data) == ["RELEASE_VERSION_REQUIRED"] and data["exit_code"] == 3
    return data["diagnostics"][0]["suggestion"]["concepts"]


def _release(*extra: str, version: str = "1.0.0") -> List[str]:
    return ["bundle", "release", "-v", version, "--approved-by", APPROVER, *extra, "--json"]


def _tags(repo: Path) -> List[str]:
    out = subprocess.run(["git", "-C", str(repo), "tag"], capture_output=True, text=True).stdout
    return sorted(out.split())


def test_a_release_names_every_concept_bundle_that_needs_a_version(repo: Path):
    concepts = _concepts(repo)
    assert concepts and all(c["reason"] == "not pinned" for c in concepts)
    assert all(c["latest_version"] is None for c in concepts)
    assert "prohibited" in {c["concept"] for c in concepts}


def test_the_dry_run_reports_exactly_what_the_release_does(repo: Path):
    fill(app(repo) / "context/project/prohibited.yaml")
    args = [x for c in _concepts(repo) for x in ("--concept", f"{c['concept']}=1.0.0")]
    before, state = files(repo), git_state(repo)

    dry = envelope(run(*_release(*args, "--dry-run")))
    assert dry["ok"], dry["diagnostics"]
    assert files(repo) == before and git_state(repo) == state
    assert dry["result"]["released"] is False

    real = envelope(run(*_release(*args)))
    assert real["ok"], real["diagnostics"]
    assert real["result"]["released"] is True

    def strip(changes: List[Dict]) -> List[Dict]:
        return [{k: v for k, v in c.items() if not (k == "ref" and c["action"] == "git-commit")}
                for c in changes]  # fmt: skip

    assert strip(dry["changes"]) == strip(real["changes"])
    tags = [c["ref"] for c in real["changes"] if c["action"] == "git-tag"]
    assert tags[-1] == "app/app-v1.0.0" and _tags(repo) == sorted(tags)
    root = yaml.safe_load((app(repo) / "bundles/project-bundle.yaml").read_text())
    assert all(str(i).endswith(":1.0.0") for i in root["imports"])
    steps = [s["step"] for s in real["result"]["steps"]]
    assert steps == ["version", "pin"] * (len(tags) - 1) + ["version"]


def test_only_changed_concept_bundles_need_a_new_version(repo: Path):
    fill(app(repo) / "context/project/prohibited.yaml")
    args = [x for c in _concepts(repo) for x in ("--concept", f"{c['concept']}=1.0.0")]
    assert envelope(run(*_release(*args)))["ok"]

    path = app(repo) / "context/project/prohibited.yaml"
    path.write_text(path.read_text().replace("personal AI accounts", "shared AI accounts"))
    data = envelope(run(*_release(version="1.1.0")))
    assert codes(data) == ["RELEASE_VERSION_REQUIRED"]
    assert data["diagnostics"][0]["suggestion"]["concepts"] == [
        {
            "concept": "prohibited",
            "bundle": "bundle:prohibited",
            "latest_version": "1.0.0",
            "reason": "changed since 1.0.0",
        }
    ]
    real = envelope(run(*_release("--concept", "prohibited=1.1.0", version="1.1.0")))
    assert real["ok"], real["diagnostics"]
    assert [c["ref"] for c in real["changes"] if c["action"] == "git-tag"] == [
        "app/prohibited-v1.1.0",
        "app/app-v1.1.0",
    ]


def test_a_failed_release_undoes_every_step(repo: Path):
    fill(app(repo) / "context/project/prohibited.yaml")
    args = [x for c in _concepts(repo) for x in ("--concept", f"{c['concept']}=1.0.0")]
    assert envelope(run(*_release(*args)))["ok"]

    path = app(repo) / "context/project/prohibited.yaml"
    path.write_text(path.read_text().replace("personal AI accounts", "shared AI accounts"))
    before, state = files(repo), git_state(repo)
    for dry in (["--dry-run"], []):
        data = envelope(run(*_release("--concept", "prohibited=1.1.0", *dry)))
        assert codes(data) == ["VERSION_EXISTS"] and data["changes"] == []
        assert files(repo) == before and git_state(repo) == state


def test_a_concept_the_root_does_not_import_is_a_usage_error(repo: Path):
    data = envelope(run(*_release("--concept", "nothing=1.0.0")))
    assert codes(data) == ["USAGE_ERROR"] and data["exit_code"] == 3
    data = envelope(run(*_release("--concept", "prohibited")))
    assert codes(data) == ["USAGE_ERROR"]
