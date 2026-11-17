"""Content digest test vectors (WP-00, spec/0.7/bundle-format.md §7.6).

The expected digests in tests/digest/expected.json were computed from the spec with jq and
shasum (tests/digest/compute_expected.sh), not with this package.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from scs_validator.digest import content_digest, digest_of
from scs_validator.resolver import resolve

VECTORS = Path(__file__).parent / "digest"
EXPECTED = json.loads((VECTORS / "expected.json").read_text(encoding="utf-8"))
DOCUMENTS = {
    "alpha": "workspace/context/project/alpha.yaml",
    "alpha-changed": "variants/alpha-changed.yaml",
    "beta": "workspace/context/project/beta.yaml",
    "gamma": "workspace/context/project/gamma.yaml",
    "first": "workspace/bundles/concepts/first.yaml",
    "second": "workspace/bundles/concepts/second.yaml",
    "project-bundle": "workspace/bundles/project-bundle.yaml",
}
BUNDLES = {
    "first": "bundles/concepts/first.yaml",
    "second": "bundles/concepts/second.yaml",
    "project-bundle": "bundles/project-bundle.yaml",
}
ALPHA = Path("context/project/alpha.yaml")


def load(relative: str):
    return yaml.safe_load((VECTORS / relative).read_text(encoding="utf-8"))


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return Path(shutil.copytree(VECTORS / "workspace", tmp_path / "workspace"))


def digests(root: Path) -> dict:
    out = {}
    for name, relative in BUNDLES.items():
        tree = resolve(root / relative)
        out[name] = content_digest(tree.root, tree.index).digest
    return out


@pytest.mark.parametrize("name", sorted(DOCUMENTS))
def test_document_digest(name: str):
    """Canonical form: sorted keys, dates and timestamps per §7.6, non-ASCII unescaped."""
    assert digest_of(load(DOCUMENTS[name])) == EXPECTED["documents"][name]


def test_content_digests_cover_sorted_scds_and_two_pinned_imports(workspace: Path):
    assert digests(workspace) == EXPECTED["content"]


def test_reordered_keys_comments_and_layout_keep_the_digest(workspace: Path):
    assert digest_of(load("variants/alpha-reformatted.yaml")) == EXPECTED["documents"]["alpha"]
    shutil.copy(VECTORS / "variants/alpha-reformatted.yaml", workspace / ALPHA)
    assert digests(workspace) == EXPECTED["content"]


def test_one_changed_value_changes_every_digest_above_it(workspace: Path):
    shutil.copy(VECTORS / "variants/alpha-changed.yaml", workspace / ALPHA)
    changed = digests(workspace)
    assert changed == EXPECTED["content_with_alpha_changed"]
    assert changed["first"] != EXPECTED["content"]["first"]
    assert changed["project-bundle"] != EXPECTED["content"]["project-bundle"]
