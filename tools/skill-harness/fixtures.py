"""Fixture Domain repositories for the scenarios, built with the SCS engine itself."""

import subprocess
from pathlib import Path

import yaml

AUTHOR = ["--author", "Pat Lee", "--email", "pat@acme-health.org"]
APPROVER = "Pat Lee <pat@acme-health.org>"
PROHIBITED = "domain/context/project/prohibited.yaml"

# A paragraph presented in the fixture manual as quoted from a standard. No SCD may contain it
# (assertion k1): SCS cites standards and never copies their text.
QUOTED_STANDARD = (
    "Records shall remain legible, readily identifiable and retrievable for the lifetime of "
    "the device, and every change to a record shall remain identifiable."
)

MANUAL = f"""# Acme Health Quality Manual (excerpt)

Document QM-01, revision C. Owner: Pat Lee, Quality Manager.

## 3. Software tools

### 3.1 AI assistants

Staff use only the company's approved AI assistant for work. Consumer AI chat services and
personal AI accounts are not used for any company or patient information.

### 3.2 Credentials

Credentials, keys, and tokens are never committed to a source repository. They are kept in
the company's secrets manager.

## 4. Records

### 4.2 Control of records

Design and test records are kept in the document control system. The portal's audit log is
never edited or deleted by application code. ISO 13485:2016 clause 4.2.5 states:

> {QUOTED_STANDARD}

### 4.3 Patient data in development

Real patient data is never used in development or test environments; synthetic data is used
instead.
"""


def run(env: dict, cwd: Path, *args: str, stdin: str | None = None) -> str:
    result = subprocess.run(
        list(args), cwd=cwd, env=env, input=stdin, capture_output=True, text=True
    )
    if result.returncode not in (0, 2):
        raise RuntimeError(f"{' '.join(args)} failed in {cwd}:\n{result.stdout}{result.stderr}")
    return result.stdout


def commit(env: dict, repo: Path) -> None:
    """Commit the fixture's edits, so each scenario starts from a clean working tree."""
    run(env, repo, "git", "add", "-A")
    if run(env, repo, "git", "status", "--porcelain").strip():
        run(env, repo, "git", "-c", "user.name=Pat Lee", "-c", "user.email=pat@acme-health.org",
            "commit", "-q", "-m", "Prepare the scenario")


def _domain(work: Path, env: dict) -> Path:
    run(env, work, "scs", "new", "domain", "acme", "--ontology", "personal", *AUTHOR,
        "--no-interactive")
    return work / "acme-context"


def _prohibitions(repo: Path, items: list[dict], created_by: str | None = None) -> None:
    path = repo / PROHIBITED
    data = yaml.safe_load(path.read_text())
    data["content"]["prohibitions"] = items
    if created_by:
        data["provenance"]["created_by"] = created_by
    path.write_text(yaml.safe_dump(data, sort_keys=False))


GOOD = [
    {"id": "NO-001", "kind": "tool",
     "subject": "consumer AI chat services and personal AI accounts",
     "reason": "Patient and company data stay in company systems."},
    {"id": "NO-002", "kind": "practice",
     "subject": "committing credentials, keys, or tokens to any repository",
     "instead": "the company secrets manager"},
]


def empty(work: Path, env: dict) -> dict:
    return {}


def draft_doc(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    run(env, repo, "scs", "new", "project", "portal", *AUTHOR, "--no-interactive")
    (repo / "sources").mkdir()
    (repo / "sources" / "quality-manual.md").write_text(MANUAL)
    return {"repo": repo, "project": "portal", "quoted": QUOTED_STANDARD}


def invalid(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, [
        {"id": "NO-001", "kind": "tool",
         "subject": "consumer AI chat services unless a manager approves"},
        {"id": "NO-001", "kind": "practice",
         "subject": "committing credentials to any repository"},
    ])
    return {"repo": repo, "errors": ["SCD_PROHIBITION_NOT_BINARY", "SCD_DUPLICATE_ENTRY_ID"]}


def ready(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD)
    run(env, repo, "scs", "intake", "record-finding", "--workspace", "domain", "--id", "rf-1",
        "--kind", "missing-protection", "--target", "scd:project:prohibited#NO-001",
        "--finding", "No approved alternative is named for personal AI accounts",
        "--decision", "deferred", "--decided-by", APPROVER)
    return {"repo": repo, "deferred": "rf-1", "deferred_words": ["alternative", "rf-1"]}


def placeholder(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD, created_by="Developer <dev@example.com>")
    return {"repo": repo}


def versioned(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD)
    domain = repo / "domain"
    run(env, domain, "scs", "bundle", "version", "--bundle", "bundles/concepts/prohibited.yaml",
        "--version", "1.0.0", "--approved-by", APPROVER)
    run(env, domain, "scs", "bundle", "pin", "prohibited", "--version", "1.0.0")
    run(env, domain, "scs", "bundle", "version", "--version", "1.0.0", "--approved-by", APPROVER)
    return {"repo": repo}


def review(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD + [
        {"id": "NO-003", "kind": "practice",
         "subject": "keeping design review records for more than 90 days",
         "reason": "Saves storage.",
         "cites": ["std:iso-13485:2016#4.2.5"]},
    ])
    run(env, repo, "scs", "intake", "set", "regulated", "true", "--workspace", "domain")
    run(env, repo, "scs", "intake", "set", "certifications", "[std:iso-13485:2016]",
        "--workspace", "domain")
    return {"repo": repo, "conflict": "NO-003", "cite": "std:iso-13485:2016"}


BUILDERS = {f.__name__: f for f in (empty, draft_doc, invalid, ready, placeholder, versioned,
                                     review)}
