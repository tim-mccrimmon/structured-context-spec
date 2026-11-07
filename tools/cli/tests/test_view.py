"""scs view: the review package (plan/0.8/bundle-review-process.md, phase 1)."""

from __future__ import annotations

import json
import shutil
from html import escape as html_escape
from pathlib import Path
from typing import Dict, Tuple

import pytest
from click.testing import CliRunner, Result
from scs_validator.resolver import resolve

from scs_tools.cli import cli
from scs_tools.compiler import compile_tree
from scs_tools.view import Source, build_view, render_html

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
EXAMPLE = REPO / "examples" / "two-tier-governance"
DOMAIN = EXAMPLE / "org" / "bundles" / "domain-bundle.yaml"
PROJECT = EXAMPLE / "infusion-pump-fw" / "bundles" / "project-bundle.yaml"
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
APPROVER = "Sam Lee <sam@structuredcontext.dev>"
CONCEPT = "bundles/concepts/prohibited.yaml"
OWNER = "{role: owner, person: Dana Fox <dana@acme.example>, title: Founder}"
SCD = "context/project/prohibited.yaml"


def run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def run_json(*args: str) -> Tuple[int, Dict]:
    result = run(*args, "--json")
    return result.exit_code, json.loads(result.stdout)


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new))


def example_html() -> str:
    view = build_view(Source(resolve(PROJECT)), Source(resolve(DOMAIN)))
    assert not view.errors, view.errors
    return render_html(view.view)


def test_every_compiled_rule_and_fact_appears_verbatim_with_its_id():
    html = example_html()
    for bundle in (DOMAIN, PROJECT):
        artifact = compile_tree(resolve(bundle)).artifact
        for entry in artifact["rules"] + artifact.get("facts", []):
            text = entry.get("rule") or entry["fact"]
            assert entry["id"] in html or entry["id"].endswith("/identity")
            assert html_escape(text) in html, text


def test_the_package_is_reproducible():
    assert example_html() == example_html()


def test_the_domain_is_marked_inherited_and_its_scds_are_linked():
    html = example_html()
    assert "inherited from the Domain" in html
    assert "href='#d-scd-project-prohibited'" in html
    assert "href='#p-scd-project-release-gates'" in html


def test_an_unverified_release_is_flagged():
    html = example_html()
    assert "could not be checked against a released version" in html
    assert "Not verified" in html


def test_content_is_escaped(tmp_path: Path):
    project = tmp_path / "p"
    shutil.copytree(PROJECT.parents[1], project)
    edit(
        project / "context" / "project" / "release-gates.yaml",
        "by a firmware engineer",
        "by <script>alert(1)</script>",
    )
    view = build_view(Source(resolve(project / "bundles" / "project-bundle.yaml")))
    assert not view.errors, view.errors
    html = render_html(view.view)
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


# --- A Domain repository with released versions -----------------------------------------


def version(bundle: str, number: str) -> None:
    code, data = run_json(
        "bundle", "version", "--bundle", bundle, "--version", number, "--approved-by", APPROVER
    )
    assert code == 0, data


def pin(bundle: Path, concept: str, number: str) -> None:
    edit(bundle, f"  - bundle:{concept}\n", f"  - bundle:{concept}:{number}\n")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """acme-context with Domain 1.0.0 and Project `app` 1.0.0, each with one prohibition."""
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = run(
        "new", "domain", "acme", "--dir", str(tmp_path), "--ontology", "personal", *AUTHOR,
        "--no-interactive",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    root = tmp_path / "acme-context"
    monkeypatch.chdir(root)
    result = run("new", "project", "app", "--ontology", "personal", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    for ws, subject in (
        (root / "domain", "shared passwords"),
        (root / "projects/app", "pastebins"),
    ):
        edit(
            ws / SCD,
            "  prohibitions: []",
            "  prohibitions:\n    - id: NO-001\n      kind: practice\n"
            f'      subject: "{subject}"',
        )
        monkeypatch.chdir(ws)
        result = run("intake", "set", "owners", OWNER)
        assert result.exit_code == 0, result.output
        version(CONCEPT, "1.0.0")
        bundle = next(p for p in (ws / "bundles").glob("*-bundle.yaml"))
        pin(bundle, "prohibited", "1.0.0")
        version(str(bundle.relative_to(ws)), "1.0.0")
    return root


def test_a_released_project_shows_its_digest_approver_and_released_domain(repo: Path):
    code, data = run_json("view", "bundles/project-bundle.yaml", "--version", "1.0.0")
    assert code == 0, data
    result = data["result"]
    assert result["verified"] and not result["draft"]
    assert result["source_digest"].startswith("sha256:")
    assert result["domain"] == {"id": "bundle:acme", "version": "1.0.0"}
    html = (repo / "projects/app" / result["path"].split("projects/app/")[1]).read_text()
    assert result["source_digest"] in html
    assert "Matches the released version" in html
    assert "Sam Lee" in html
    assert "Prohibited: pastebins." in html
    assert "Prohibited: shared passwords." in html
    assert "projects/app/bundles/app-v1.0.0-MANIFEST.yaml" not in html


def test_a_changed_rule_after_release_cannot_be_shown_as_that_version(repo: Path):
    edit(repo / "projects/app" / SCD, "pastebins", "public pastebins")
    code, data = run_json("view", "bundles/project-bundle.yaml", "--allow-draft")
    assert code == 1
    messages = [d["message"] for d in data["diagnostics"] if d["code"] == "COMPILE_ERROR"]
    assert any("has changed since it was versioned" in m for m in messages), messages


def test_a_draft_needs_allow_draft_and_is_marked(repo: Path, tmp_path: Path):
    # After a release the working bundle is back at DRAFT.
    code, data = run_json("view", "bundles/project-bundle.yaml")
    assert code == 1
    out = tmp_path / "draft.html"
    code, data = run_json("view", "bundles/project-bundle.yaml", "--allow-draft", "-o", str(out))
    assert code == 0, data
    assert data["result"]["draft"]
    assert "cannot be certified" in out.read_text()


def test_no_released_domain_is_a_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    run("new", "domain", "solo", "--dir", str(tmp_path), "--ontology", "personal", *AUTHOR,
        "--no-interactive")  # fmt: skip
    monkeypatch.chdir(tmp_path / "solo-context")
    run("new", "project", "app", "--ontology", "personal", *AUTHOR, "--no-interactive")
    ws = tmp_path / "solo-context/projects/app"
    edit(
        ws / SCD,
        "  prohibitions: []",
        '  prohibitions:\n    - id: NO-001\n      kind: tool\n      subject: "pastebins"',
    )
    monkeypatch.chdir(ws)
    code, data = run_json("view", "bundles/project-bundle.yaml", "--allow-draft", "--dry-run")
    assert code == 0, data
    assert "VIEW_DOMAIN_UNAVAILABLE" in [d["code"] for d in data["diagnostics"]]
    assert data["result"]["domain"] is None and not data["changes"][0]["path"].startswith("/")


def test_domain_version_selects_a_release_and_unknown_versions_fail(repo: Path):
    code, data = run_json("view", "bundles/project-bundle.yaml", "--version", "1.0.0",
                          "--domain-version", "1.0.0", "--dry-run")  # fmt: skip
    assert code == 0 and data["result"]["domain"]["version"] == "1.0.0"
    code, data = run_json("view", "bundles/project-bundle.yaml", "--domain-version", "9.9.9")
    assert code != 0
    assert "VERSION_NOT_FOUND" in [d["code"] for d in data["diagnostics"]]


def test_each_section_shows_its_owner_as_recorded_with_the_release(repo: Path):
    code, data = run_json("view", "bundles/project-bundle.yaml", "--version", "1.0.0")
    assert code == 0, data
    html = (repo / "projects/app/dist/app-1.0.0-review.html").read_text()
    assert "<h2>Section owners</h2>" in html
    assert "Founder, Dana Fox &lt;dana@acme.example&gt;" in html
    assert "The one section has an accountable owner." in html

    # The release records who held the role then; a later change shows in the next package.
    run("intake", "set", "owners", "{role: owner, person: Lee Wu <lee@acme.example>}")
    run_json("view", "bundles/project-bundle.yaml", "--version", "1.0.0")
    assert "Dana Fox" in (repo / "projects/app/dist/app-1.0.0-review.html").read_text()


def test_a_section_no_one_holds_is_flagged(repo: Path, tmp_path: Path):
    intake = repo / "projects/app/intake.yaml"
    intake.write_text(intake.read_text().split("owners:")[0])
    out = tmp_path / "draft.html"
    code, data = run_json("view", "bundles/project-bundle.yaml", "--allow-draft", "-o", str(out))
    assert code == 0, data
    html = out.read_text()
    assert "No one holds the role owner" in html
    assert "The one section has no one accountable for it." in html
