"""Units behind lifecycle integrity (WP-14): placeholder provenance, resolver selection, empty
SCDs, and version names. The end-to-end cases are in tools/cli/tests/test_lifecycle.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scs_validator.checks.empty_scds import is_empty
from scs_validator.names import VERSION_TAG_RE, is_snapshot, manifest_name, snapshot_name
from scs_validator.provenance import is_placeholder
from scs_validator.resolver import Index


@pytest.mark.parametrize(
    "created_by",
    [
        "CI <ci@example.com>",
        "developer",
        "Developer <dev@acme.org>",
        " <jane@acme.org>",
        "jdoe@example.org",
        "Jane <jane@mail.example.net>",
        "Jane <jane@acme.example>",
        "scs-tools <noreply@scs.invalid>",
    ],
)
def test_placeholders(created_by: str):
    assert is_placeholder(created_by)


@pytest.mark.parametrize(
    "created_by",
    [
        "scs-maintainers",
        "Tim McCrimmon",
        "security-team@medtech.com",
        "Jane Doe <jane@structuredcontext.dev>",
        "role:quality-lead",
        "",
        None,
        "jane@example.community",
    ],
)
def test_true_values(created_by):
    assert not is_placeholder(created_by)


def test_version_names():
    assert snapshot_name("security", "1.2.3") == "security-v1.2.3.yaml"
    assert manifest_name("security", "1.2.3") == "security-v1.2.3-MANIFEST.yaml"
    assert is_snapshot(Path("bundles/concepts/security-v1.2.3.yaml"))
    assert not is_snapshot(Path("bundles/concepts/security.yaml"))
    match = VERSION_TAG_RE.match("app/security-v1.2.3")
    assert match and match.group("workspace", "name", "version") == ("app", "security", "1.2.3")
    assert VERSION_TAG_RE.match("v1.2.3") is None


def _bundle(path: Path, version: str, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"id": "bundle:security", "type": "concept", "version": version, "title": title}
    path.write_text(yaml.safe_dump(data))


def test_unpinned_resolves_to_the_working_file_and_pinned_to_the_snapshot(tmp_path: Path):
    """D-17. The snapshot sorts before the working file, so file order does not decide it."""
    concepts = tmp_path / "bundles" / "concepts"
    _bundle(concepts / "security-v1.0.0.yaml", "1.0.0", "released")
    _bundle(concepts / "security.yaml", "DRAFT", "working")
    index = Index([tmp_path])

    unpinned, mismatch = index.find_bundle("bundle:security")
    assert unpinned is not None and unpinned.data["title"] == "working" and not mismatch
    pinned, mismatch = index.find_bundle("bundle:security:1.0.0")
    assert pinned is not None and pinned.data["title"] == "released" and not mismatch
    missing, mismatch = index.find_bundle("bundle:security:2.0.0")
    assert mismatch


def test_a_06_layout_with_only_snapshots_resolves_unpinned_to_a_snapshot(tmp_path: Path):
    _bundle(tmp_path / "bundles" / "concepts" / "security-v1.0.0.yaml", "1.0.0", "released")
    found, _ = Index([tmp_path]).find_bundle("bundle:security")
    assert found is not None and found.data["title"] == "released"


@pytest.mark.parametrize(
    "content, empty",
    [
        (None, True),
        ({"summary": "only a summary"}, True),
        ({"prohibitions": [], "directives": [], "facts": []}, True),
        ({"facts": [{"id": "F-1", "fact": "x"}]}, False),
        ({"directives": [{"id": "D-1", "directive": "x"}]}, False),
    ],
)
def test_empty_scds(content, empty: bool):
    assert is_empty({"id": "scd:project:x", "content": content}) is empty
