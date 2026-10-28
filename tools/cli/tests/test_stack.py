"""`scs stack` (WP-16, RFC 0002 section 13, runtime-artifact.md §5)."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml
from click.testing import CliRunner

from scs_tools.cli import cli

EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "two-tier-governance" / "compiled"


def artifact(
    name: str,
    kind: str = "domain",
    version: str = "1.0.0",
    rules: Optional[List[str]] = None,
    facts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "scs_runtime": "0.7",
        "id": f"bundle:{name}",
        "type": kind,
        "version": version,
        "title": name.title(),
        "sources": [],
        "rules": [
            {
                "id": f"{name}/identity",
                "rule": f'When asked which bundles are active, state: "{name} {version}".',
            }
        ],
    }
    if not version.startswith("DRAFT"):
        data["source_digest"] = "sha256:" + "0" * 64
    for i, text in enumerate(rules or [], start=1):
        data["rules"].append({"id": f"{name}/rules/R-{i:03d}", "rule": text})
    if facts:
        data["facts"] = [
            {"id": f"{name}/facts/F-{i:03d}", "fact": text} for i, text in enumerate(facts, start=1)
        ]
    return data


def write(directory: Path, name: str, data: Any) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def run(*args: str):
    result = CliRunner().invoke(cli, ["stack", *args, "--json"])
    return result, json.loads(result.stdout)


def codes(envelope: Dict[str, Any]) -> List[str]:
    return [d["code"] for d in envelope["diagnostics"]]


def snapshot(root: Path) -> Dict[str, bytes]:
    return {str(p): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.fixture
def layers(tmp_path: Path, monkeypatch) -> List[Path]:
    monkeypatch.chdir(tmp_path)
    personal = write(
        tmp_path / "jdoe-context",
        "jdoe",
        artifact("jdoe", rules=["Prohibited: pasting secrets into a chat."]),
    )
    company = write(
        tmp_path / "acme-context",
        "acme",
        artifact(
            "acme",
            rules=[
                "Prohibited: consumer AI accounts. Use instead: the company AI service.",
                "Cite rule ids.",
            ],
            facts=["Acme builds catheters."],
        ),
    )
    project = write(
        tmp_path / "acme-context" / "projects",
        "pump",
        artifact("pump", kind="project", version="0.3.0", rules=["Write tests first."]),
    )
    return [personal, company, project]


def test_a_stack_lists_layers_and_every_rule_in_order(layers: List[Path], tmp_path: Path):
    before = snapshot(tmp_path)
    result, envelope = run(*map(str, layers))
    assert result.exit_code == 0, result.output
    assert envelope["ok"] and envelope["command"] == "stack" and envelope["changes"] == []
    assert snapshot(tmp_path) == before

    stacked = envelope["result"]
    assert [layer["id"] for layer in stacked["layers"]] == [
        "bundle:jdoe",
        "bundle:acme",
        "bundle:pump",
    ]
    assert [layer["position"] for layer in stacked["layers"]] == [1, 2, 3]
    assert stacked["layers"][0]["path"] == "jdoe-context/jdoe.yaml"
    assert stacked["layers"][0]["source_digest"].startswith("sha256:")

    expected = []
    for position, path in enumerate(layers, start=1):
        data = yaml.safe_load(path.read_text())
        expected += [(position, r["id"], r["rule"]) for r in data["rules"]]
        expected += [(position, f["id"], f["fact"]) for f in data.get("facts", [])]
    got = [(e["layer"], e["id"], e.get("rule", e.get("fact"))) for e in stacked["context"]]
    assert got == expected


def test_the_order_given_is_the_order_reported(layers: List[Path]):
    _, envelope = run(*map(str, reversed(layers)))
    assert [layer["id"] for layer in envelope["result"]["layers"]] == [
        "bundle:pump",
        "bundle:acme",
        "bundle:jdoe",
    ]
    assert envelope["result"]["context"][0]["id"] == "pump/identity"


def test_a_single_artifact_is_a_stack_of_one(layers: List[Path]):
    result, envelope = run(str(layers[0]))
    assert result.exit_code == 0
    assert len(envelope["result"]["layers"]) == 1


def test_a_bundle_in_two_layers_is_an_error(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old = write(tmp_path / "a", "acme", artifact("acme", version="1.0.0"))
    new = write(tmp_path / "b", "acme", artifact("acme", version="1.1.0"))
    result, envelope = run(str(old), str(new))
    assert result.exit_code == 1
    assert codes(envelope) == ["STACK_BUNDLE_REPEATED"]
    assert "layer 1" in envelope["diagnostics"][0]["message"]
    assert "layer 2" in envelope["diagnostics"][0]["message"]


def test_a_directive_naming_another_layers_prohibition_is_a_warning(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    outer = write(tmp_path, "acme", artifact("acme", rules=["Prohibited: Consumer AI accounts."]))
    inner = write(
        tmp_path,
        "pump",
        artifact("pump", kind="project", rules=["Use consumer ai accounts for quick drafts."]),
    )
    result, envelope = run(str(outer), str(inner))
    assert result.exit_code == 0
    assert codes(envelope) == ["STACK_PROHIBITION_DIRECTED"]
    message = envelope["diagnostics"][0]["message"]
    assert "pump/rules/R-001" in message and "acme/rules/R-001" in message

    strict = CliRunner().invoke(cli, ["stack", str(outer), str(inner), "--strict", "--json"])
    assert strict.exit_code == 2
    assert json.loads(strict.stdout)["ok"] is False


def test_a_prohibition_and_directive_in_the_same_layer_are_not_reported(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    one = write(
        tmp_path,
        "acme",
        artifact(
            "acme", rules=["Prohibited: consumer AI accounts.", "Never use consumer AI accounts."]
        ),
    )
    other = write(tmp_path, "pump", artifact("pump", kind="project", rules=["Write tests."]))
    _, envelope = run(str(one), str(other))
    assert "STACK_PROHIBITION_DIRECTED" not in codes(envelope)


def test_the_use_instead_clause_is_not_part_of_the_subject(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    outer = write(
        tmp_path,
        "acme",
        artifact(
            "acme", rules=["Prohibited: consumer AI accounts. Use instead: the company AI service."]
        ),
    )
    inner = write(
        tmp_path,
        "pump",
        artifact("pump", kind="project", rules=["Draft in the company AI service."]),
    )
    _, envelope = run(str(outer), str(inner))
    assert codes(envelope) == []


def test_identical_text_in_two_layers_is_information(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shared = "Name the rule id when you decline."
    a = write(tmp_path, "acme", artifact("acme", rules=[shared], facts=["Acme is in Minnesota."]))
    b = write(tmp_path, "beta", artifact("beta", rules=[shared], facts=["Acme is in Minnesota."]))
    result, envelope = run(str(a), str(b))
    assert result.exit_code == 0
    assert codes(envelope) == ["STACK_RULE_DUPLICATE", "STACK_RULE_DUPLICATE"]
    assert all(d["severity"] == "info" for d in envelope["diagnostics"])
    assert len(envelope["result"]["context"]) == 2 * 3  # nothing dropped


def test_a_draft_layer_is_information(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    draft = write(
        tmp_path, "acme", artifact("acme", version="DRAFT+0123abcd", rules=["Cite rule ids."])
    )
    result, envelope = run(str(draft))
    assert result.exit_code == 0
    assert codes(envelope) == ["STACK_LAYER_DRAFT"]
    assert "source_digest" not in envelope["result"]["layers"][0]


def test_an_input_that_is_not_an_artifact_is_rejected(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bundle = write(
        tmp_path, "domain-bundle", {"id": "bundle:acme", "type": "domain", "version": "DRAFT"}
    )
    broken = tmp_path / "broken.yaml"
    broken.write_text("rules: [unclosed\n", encoding="utf-8")
    good = write(tmp_path, "pump", artifact("pump", kind="project", rules=["Write tests."]))
    result, envelope = run(str(bundle), str(broken), str(good))
    assert result.exit_code == 1
    assert codes(envelope) == ["STACK_ARTIFACT_INVALID", "STACK_ARTIFACT_INVALID"]
    assert envelope["result"] == {"stacked": False}


def test_a_missing_artifact_is_a_file_error(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result, envelope = run(str(tmp_path / "nope.yaml"))
    assert result.exit_code == 4
    assert codes(envelope) == ["FILE_NOT_FOUND"]


def test_no_artifacts_is_a_usage_error(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["stack", "--json"])
    assert result.exit_code == 3
    assert json.loads(result.stdout)["diagnostics"][0]["code"] == "USAGE_ERROR"


def test_artifacts_from_other_directories_are_read(layers: List[Path], tmp_path: Path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    result, envelope = run(*(str(p.resolve()) for p in layers))
    assert result.exit_code == 0
    assert envelope["result"]["layers"][0]["path"].endswith("jdoe-context/jdoe.yaml")


def test_the_compiled_examples_stack(monkeypatch):
    monkeypatch.chdir(EXAMPLES)
    result, envelope = run("global.yaml", "projects/infusion-pump-fw.yaml")
    assert result.exit_code == 0, result.output
    assert [layer["type"] for layer in envelope["result"]["layers"]] == ["domain", "project"]


def test_human_output_shows_layers_and_rules(layers: List[Path]):
    result = CliRunner().invoke(cli, ["stack", *map(str, layers)])
    assert result.exit_code == 0, result.output
    assert "Stack of 3 layers, outermost first:" in result.output
    assert "[rule] acme/rules/R-002: Cite rule ids." in result.output
    assert "[fact] acme/facts/F-001: Acme builds catheters." in result.output
