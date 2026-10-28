"""`scs bundle diff` (WP-08, RFC 0002 section 7, D-41): one golden result per change kind, the
D-41 baselines, determinism, and machine-mode conformance."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
import pytest
from click.testing import CliRunner, Result

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
ENVELOPE_SCHEMA = json.loads((SCHEMA / "cli" / "envelope-schema.json").read_text())
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
APPROVER = "Sam Lee <sam@structuredcontext.dev>"
CONCEPT = "bundles/concepts/prohibited.yaml"
ROOT = "bundles/project-bundle.yaml"
SCD = "context/project/prohibited.yaml"
SCD_ID = "scd:project:prohibited"
# Plain git for test setup, past any global config (signing, hooks).
PLAIN = [
    "-c", "user.name=Test", "-c", "user.email=test@structuredcontext.dev",
    "-c", "commit.gpgsign=false", "-c", "tag.gpgSign=false", "-c", "tag.forceSignAnnotated=false",
    "-c", "core.hooksPath=/dev/null",
]  # fmt: skip
NO_001 = (
    "    - id: NO-001\n      kind: tool\n"
    '      subject: "personal AI accounts"\n'
    "      cites: [std:iso-27001:2022#A.5.10]\n"
)


def run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new))


def envelope(result: Result) -> Dict[str, Any]:
    data = json.loads(result.stdout)
    jsonschema.validate(data, ENVELOPE_SCHEMA)
    assert data["exit_code"] == result.exit_code
    assert data["command"] == "bundle diff"
    assert data["changes"] == []
    return data


def diff(*args: str) -> Dict[str, Any]:
    result = run("bundle", "diff", *args, "--json")
    data = envelope(result)
    assert result.exit_code == 0, data
    return data["result"]


def version(bundle: str, number: str) -> None:
    result = run(
        "bundle", "version", "--bundle", bundle, "--version", number, "--approved-by", APPROVER,
        "--json",
    )  # fmt: skip
    assert result.exit_code == 0, result.stdout


def snapshot(root: Path) -> Dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and ".git" not in p.relative_to(root).parts
    }


@pytest.fixture
def ws(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Project `app` of a personal Domain repository; its `prohibited` concept has NO-001."""
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = run(
        "new", "domain", "acme", "--dir", str(tmp_path), "--ontology", "personal", *AUTHOR,
        "--no-interactive",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    monkeypatch.chdir(tmp_path / "acme-context")
    result = run("new", "project", "app", "--ontology", "personal", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    app = tmp_path / "acme-context" / "projects" / "app"
    edit(app / SCD, "  prohibitions: []\n", "  prohibitions:\n" + NO_001)
    monkeypatch.chdir(app)
    return app


def empty_groups() -> Dict[str, Any]:
    return {
        "scds": {"added": [], "removed": []},
        "items": {"added": [], "removed": [], "changed": []},
        "citations": {"added": [], "removed": []},
        "imports": {"added": [], "removed": [], "repinned": []},
    }


def changes_only(result: Dict[str, Any]) -> Dict[str, Any]:
    return {k: result[k] for k in ("scds", "items", "citations", "imports")}


def expect(**groups: Dict[str, List[Any]]) -> Dict[str, Any]:
    out = empty_groups()
    for name, kinds in groups.items():
        out[name].update(kinds)
    return out


# ------------------------------------------------------------------------- baselines


def test_a_first_version_diffs_from_empty(ws: Path):
    result = diff(CONCEPT)
    assert result["from"] == {"version": "empty", "source": "empty"}
    assert result["to"] == {"version": "working", "source": "working"}
    assert result["changed"] is True
    assert changes_only(result) == expect(
        scds={"added": [SCD_ID]},
        items={"added": [{"scd": SCD_ID, "kind": "prohibitions", "id": "NO-001"}]},
        citations={
            "added": [{"scd": SCD_ID, "cite": "std:iso-27001:2022#A.5.10", "item": "NO-001"}]
        },
    )


def test_the_default_from_is_the_latest_version_and_unchanged_is_empty(ws: Path):
    version(CONCEPT, "1.0.0")
    result = diff(CONCEPT)
    assert result["from"] == {
        "version": "1.0.0",
        "source": "tag",
        "tag": "app/prohibited-v1.0.0",
    }
    assert result["changed"] is False
    assert changes_only(result) == empty_groups()


def test_the_latest_version_is_chosen_by_semver_not_by_name(ws: Path):
    version(CONCEPT, "1.9.0")
    edit(ws / SCD, "personal AI accounts", "personal AI accounts and consumer chatbots")
    version(CONCEPT, "1.10.0")
    assert diff(CONCEPT)["from"]["version"] == "1.10.0"


def test_an_explicit_from_with_no_tag_is_an_error(ws: Path):
    result = run("bundle", "diff", CONCEPT, "--from", "2.0.0", "--json")
    assert result.exit_code == 1
    data = envelope(result)
    assert [d["code"] for d in data["diagnostics"]] == ["DIFF_VERSION_NOT_FOUND"]
    assert "app/prohibited-v2.0.0" in data["diagnostics"][0]["message"]


def test_a_to_version_with_no_tag_is_an_error(ws: Path):
    version(CONCEPT, "1.0.0")
    result = run("bundle", "diff", CONCEPT, "--to", "1.1.0", "--json")
    assert result.exit_code == 1
    assert [d["code"] for d in envelope(result)["diagnostics"]] == ["DIFF_VERSION_NOT_FOUND"]


def test_a_pre_0_7_only_bundle_diffs_from_its_snapshot(ws: Path):
    legacy = ws / "bundles" / "concepts" / "prohibited-v1.0.0.yaml"
    legacy.write_text((ws / CONCEPT).read_text().replace('version: "DRAFT"', 'version: "1.0.0"'))
    other = ws / "context" / "project" / "extra.yaml"
    other.write_text((ws / SCD).read_text().replace(SCD_ID, "scd:project:extra"))
    edit(ws / CONCEPT, f"  - {SCD_ID}\n", f"  - {SCD_ID}\n  - scd:project:extra\n")

    data = envelope(run("bundle", "diff", CONCEPT, "--json"))
    assert data["exit_code"] == 0
    assert [d["code"] for d in data["diagnostics"]] == ["DIFF_LEGACY_BASELINE"]
    assert data["diagnostics"][0]["severity"] == "info"
    result = data["result"]
    assert result["from"] == {
        "version": "1.0.0",
        "source": "legacy-snapshot",
        "path": "projects/app/bundles/concepts/prohibited-v1.0.0.yaml",
    }
    assert result["scds"]["added"] == ["scd:project:extra"]
    assert result["not_compared"] == [SCD_ID]
    assert {"scd": "scd:project:extra", "kind": "prohibitions", "id": "NO-001"} in result["items"][
        "added"
    ]


def test_a_0_7_version_is_preferred_to_a_legacy_snapshot(ws: Path):
    legacy = ws / "bundles" / "concepts" / "prohibited-v0.9.0.yaml"
    legacy.write_text((ws / CONCEPT).read_text().replace('version: "DRAFT"', 'version: "0.9.0"'))
    version(CONCEPT, "1.0.0")
    data = envelope(run("bundle", "diff", CONCEPT, "--json"))
    assert data["diagnostics"] == []
    assert data["result"]["from"]["source"] == "tag"


# ------------------------------------------------------------- one golden per change kind


def test_scd_added(ws: Path):
    version(CONCEPT, "1.0.0")
    (ws / "context" / "project" / "extra.yaml").write_text(
        (ws / SCD).read_text().replace(SCD_ID, "scd:project:extra").replace(NO_001, "")
        .replace("  prohibitions:\n", "  prohibitions: []\n")
    )  # fmt: skip
    edit(ws / CONCEPT, f"  - {SCD_ID}\n", f"  - {SCD_ID}\n  - scd:project:extra\n")
    assert changes_only(diff(CONCEPT)) == expect(scds={"added": ["scd:project:extra"]})


def test_scd_removed(ws: Path):
    (ws / "context" / "project" / "extra.yaml").write_text(
        (ws / SCD).read_text().replace(SCD_ID, "scd:project:extra")
    )
    edit(ws / CONCEPT, f"  - {SCD_ID}\n", f"  - {SCD_ID}\n  - scd:project:extra\n")
    version(CONCEPT, "1.0.0")
    assert run("bundle", "remove-scd", "scd:project:extra", "--json").exit_code == 0
    assert changes_only(diff(CONCEPT)) == expect(
        scds={"removed": ["scd:project:extra"]},
        items={"removed": [{"scd": "scd:project:extra", "kind": "prohibitions", "id": "NO-001"}]},
        citations={
            "removed": [
                {"scd": "scd:project:extra", "cite": "std:iso-27001:2022#A.5.10", "item": "NO-001"}
            ]
        },
    )


def test_item_added(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(
        ws / SCD,
        NO_001,
        NO_001 + '    - id: NO-002\n      kind: practice\n      subject: "sharing passwords"\n',
    )
    assert changes_only(diff(CONCEPT)) == expect(
        items={"added": [{"scd": SCD_ID, "kind": "prohibitions", "id": "NO-002"}]}
    )


def test_item_removed(ws: Path):
    edit(
        ws / SCD,
        NO_001,
        NO_001 + '    - id: NO-002\n      kind: practice\n      subject: "sharing passwords"\n',
    )
    version(CONCEPT, "1.0.0")
    edit(
        ws / SCD, '    - id: NO-002\n      kind: practice\n      subject: "sharing passwords"\n', ""
    )
    assert changes_only(diff(CONCEPT)) == expect(
        items={"removed": [{"scd": SCD_ID, "kind": "prohibitions", "id": "NO-002"}]}
    )


def test_item_changed_names_the_fields(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"personal AI accounts and consumer chatbots"')
    edit(ws / SCD, "      kind: tool\n", "      kind: tool\n      instead: the company assistant\n")
    assert changes_only(diff(CONCEPT)) == expect(
        items={
            "changed": [
                {
                    "scd": SCD_ID,
                    "kind": "prohibitions",
                    "id": "NO-001",
                    "fields": ["instead", "subject"],
                }
            ]
        }
    )


def test_citation_added(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, "#A.5.10]", "#A.5.10, std:hipaa#164.312(a)(1)]")
    result = changes_only(diff(CONCEPT))
    assert result["citations"] == {
        "added": [{"scd": SCD_ID, "cite": "std:hipaa#164.312(a)(1)", "item": "NO-001"}],
        "removed": [],
    }
    assert result["items"]["changed"] == [
        {"scd": SCD_ID, "kind": "prohibitions", "id": "NO-001", "fields": ["cites"]}
    ]


def test_citation_removed_at_the_scd_level(ws: Path):
    edit(ws / SCD, "\nprovenance:", "\ncites:\n  - std:iso-27001:2022\nprovenance:")
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, "\ncites:\n  - std:iso-27001:2022\nprovenance:", "\nprovenance:")
    assert changes_only(diff(CONCEPT)) == expect(
        citations={"removed": [{"scd": SCD_ID, "cite": "std:iso-27001:2022"}]}
    )


def test_import_repinned(ws: Path):
    version(CONCEPT, "1.0.0")
    assert run("bundle", "pin", "prohibited", "--version", "1.0.0", "--json").exit_code == 0
    version(ROOT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"personal AI accounts and consumer chatbots"')
    version(CONCEPT, "1.1.0")
    assert run("bundle", "pin", "prohibited", "--version", "1.1.0", "--json").exit_code == 0
    result = diff(ROOT)
    assert result["imports"] == {
        "added": [],
        "removed": [],
        "repinned": [
            {"bundle": "bundle:app", "import": "bundle:prohibited", "from": "1.0.0", "to": "1.1.0"}
        ],
    }
    assert result["items"]["changed"] == [
        {"scd": SCD_ID, "kind": "prohibitions", "id": "NO-001", "fields": ["subject"]}
    ]


def test_import_added_and_removed(ws: Path):
    assert (
        run("add", "bundle", "groceries", "--new", "--title", "Groceries", *AUTHOR).exit_code == 0
    )
    result = diff(ROOT)
    assert {"bundle": "bundle:app", "ref": "bundle:groceries"} in result["imports"]["added"]
    assert "scd:project:groceries" in result["scds"]["added"]


# ---------------------------------------------------------------------- two versions


def test_two_versions_compare_tagged_content_not_the_working_tree(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"personal AI accounts and consumer chatbots"')
    version(CONCEPT, "1.1.0")
    edit(ws / SCD, "kind: tool", "kind: practice")  # a working edit after 1.1.0
    result = diff(CONCEPT, "--from", "1.0.0", "--to", "1.1.0")
    assert result["to"] == {"version": "1.1.0", "source": "tag", "tag": "app/prohibited-v1.1.0"}
    assert result["items"]["changed"] == [
        {"scd": SCD_ID, "kind": "prohibitions", "id": "NO-001", "fields": ["subject"]}
    ]


def test_a_moved_tag_fails_its_integrity_check(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"anything else"')
    git = ["git", *PLAIN]
    subprocess.run([*git, "commit", "-qam", "edit"], check=True, cwd=ws)
    subprocess.run(
        [*git, "tag", "-f", "-a", "-m", "moved", "app/prohibited-v1.0.0"],
        check=True,
        cwd=ws,
        capture_output=True,
    )
    result = run("bundle", "diff", CONCEPT, "--json")
    data = envelope(result)
    assert result.exit_code == 1
    assert data["result"] == {"diffed": False}
    assert "CONTENT_DIGEST_MISMATCH" in [d["code"] for d in data["diagnostics"]]


# ---------------------------------------------------------------- conformance, determinism


def test_identical_input_gives_byte_identical_output(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"personal AI accounts and consumer chatbots"')
    for args in (["--json"], []):
        first = run("bundle", "diff", ROOT, *args)
        second = run("bundle", "diff", ROOT, *args)
        assert first.exit_code == 0, first.output
        assert first.stdout == second.stdout


def test_diff_writes_nothing(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, "kind: tool", "kind: practice")
    repo = ws.parent.parent
    before = snapshot(repo)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True).stdout
    diff(ROOT)
    run("bundle", "diff", ROOT)
    assert snapshot(repo) == before
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True).stdout == head
    )


def test_the_human_summary(ws: Path):
    version(CONCEPT, "1.0.0")
    edit(ws / SCD, '"personal AI accounts"', '"personal AI accounts and consumer chatbots"')
    result = run("bundle", "diff", CONCEPT)
    assert result.exit_code == 0, result.output
    assert result.stdout == (
        "bundle:prohibited: 1.0.0 -> working\n"
        "  ~ scd:project:prohibited prohibition NO-001 (subject)\n"
    )


def test_the_root_bundle_is_the_default(ws: Path):
    assert diff()["bundle"] == "bundle:app"


@pytest.mark.parametrize("args", [["--from", "1.0"], ["--to", "latest"]])
def test_a_malformed_version_is_a_usage_error(ws: Path, args: List[str]):
    result = run("bundle", "diff", CONCEPT, *args, "--json")
    assert result.exit_code == 3
    assert [d["code"] for d in envelope(result)["diagnostics"]] == ["VERSION_INVALID"]


def test_diff_is_not_a_top_level_command():
    assert run("diff").exit_code != 0
