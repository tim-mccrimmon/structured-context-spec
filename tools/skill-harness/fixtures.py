"""Fixture Domain repositories for the scenarios, built with the SCS engine itself.

A builder returns what the checks need to know about its fixture. `documents` lists files the
simulated user holds outside the work folder; the harness copies them into the `sources/`
folder the user is told to use (assertion o), as the user would.
"""

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


POLICY = """# Acme Health AI Usage Policy

Policy POL-07, version 2. Owner: Sam Ortiz, CTO. Approved by Morgan Chen, CEO.

## 1. Scope

This policy covers every use of AI tools for Acme Health work, by every employee and contractor.

## 2. Roles

- Morgan Chen, CEO: approves this policy.
- Sam Ortiz, CTO: owns this policy and the list of approved AI tools.
- Pat Lee, Quality Manager: approves changes to the rules AI tools follow.

## 3. Rules

3.1 Use only the AI assistant the company has approved. Consumer AI chat services and personal
AI accounts are not used for company or patient information.

3.2 Patient data (PHI) is never entered into an AI tool, approved or not.

3.3 Code an AI tool writes is reviewed by a developer before it is merged.

3.4 Real patient data is never used in development or test environments.
"""

BRIEF = """# Patient portal: project brief

Owner: Riley Park, product lead.

Patients use the portal to view their records, appointments, and messages from their clinic.
It is a web and mobile app, cloud hosted. It handles PHI and PII; no payment data. No software
safety class applies.

Team: Riley Park (product lead), Jordan Kim (developer), Avery Shah (developer), Pat Lee
(quality reviewer). Morgan Chen is the business owner.

The first release covers viewing records and appointments. Messaging comes in the second
release. Developers use the company's approved AI assistant to draft code and tests.
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


def _documents(work: Path, files: dict[str, str]) -> list[str]:
    """Files the simulated user holds, outside the work folder."""
    folder = work.parent / "documents"
    folder.mkdir(exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text)
    return [str(folder / name) for name in files]


def _release(env: dict, repo: Path, workspace: str = "domain") -> None:
    """Version the workspace's concept bundle and its root as 1.0.0."""
    folder = repo / workspace
    # A personal workspace's one owner role (D-92) must be held before versioning.
    run(env, folder, "scs", "intake", "set", "owners", f"{{role: owner, person: {APPROVER}}}")
    run(env, folder, "scs", "bundle", "version", "--bundle", "bundles/concepts/prohibited.yaml",
        "--version", "1.0.0", "--approved-by", APPROVER)
    run(env, folder, "scs", "bundle", "pin", "prohibited", "--version", "1.0.0")
    run(env, folder, "scs", "bundle", "version", "--version", "1.0.0", "--approved-by", APPROVER)


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


def _intake(env: dict, repo: Path, workspace: str, fields: dict[str, str]) -> None:
    for field, value in fields.items():
        run(env, repo, "scs", "intake", "set", field, value, "--workspace", workspace)


DOMAIN_INTAKE = {"audience": "organization", "regulated": "true",
                 "organization": "{name: Acme Health, products: [patient portal]}"}


def _released(work: Path, env: dict, extra: list[dict] | None = None) -> Path:
    """A Domain with an intake record and a released version 1.0.0."""
    repo = _domain(work, env)
    _prohibitions(repo, GOOD + (extra or []))
    _intake(env, repo, "domain", DOMAIN_INTAKE)
    commit(env, repo)
    _release(env, repo)
    return repo


def empty(work: Path, env: dict) -> dict:
    """Nothing yet: the user has only their AI usage policy (domain-init)."""
    docs = _documents(work, {"ai-usage-policy.md": POLICY})
    return {"documents": docs, "sources": "acme-health-context/domain/sources"}


def resume(work: Path, env: dict) -> dict:
    """A Domain set up yesterday and left partway: routing answers and the policy recorded, no
    people, no approvers, nothing drafted (domain-resume)."""
    repo = _domain(work, env)
    (repo / "domain" / "sources" / "ai-usage-policy.md").write_text(POLICY)
    _intake(env, repo, "domain", {
        "audience": "organization", "regulated": "true",
        "source_documents": "{id: doc-ai-policy, title: AI Usage Policy, "
                            "path: sources/ai-usage-policy.md}"})
    return {"repo": repo, "done": ["policy", "audience"],
            "open": ["people", "approver", "draft"]}


def unreleased(work: Path, env: dict) -> dict:
    """A Domain drafted but never versioned: a Project cannot start yet (project-gate)."""
    repo = _domain(work, env)
    _prohibitions(repo, GOOD)
    _intake(env, repo, "domain", DOMAIN_INTAKE)
    return {"repo": repo, "unreleased": True}


def released(work: Path, env: dict) -> dict:
    """A released Domain, and the project brief in the user's hands (project-init)."""
    repo = _released(work, env)
    docs = _documents(work, {"portal-brief.md": BRIEF})
    return {"repo": repo, "documents": docs, "sources": "acme-context/projects/portal/sources",
            "project": "portal"}


def draft_doc(work: Path, env: dict) -> dict:
    repo = _released(work, env)
    run(env, repo, "scs", "new", "project", "portal", *AUTHOR, "--no-interactive")
    (repo / "projects" / "portal" / "sources" / "quality-manual.md").write_text(MANUAL)
    return {"repo": repo, "project": "portal", "quoted": QUOTED_STANDARD}


BLOCKING = {"id": "NO-003", "kind": "practice",
            "subject": "AI tools writing code that reads, displays, or stores patient records",
            "reason": "Keeps PHI away from AI tools."}


def project_review(work: Path, env: dict) -> dict:
    """A released Domain with a rule that blocks the portal's own work, and a drafted portal
    Project: the review should record the conflict in the Project and leave the Domain alone."""
    repo = _released(work, env, extra=[BLOCKING])
    run(env, repo, "scs", "new", "project", "portal", *AUTHOR, "--no-interactive")
    path = repo / "projects" / "portal" / "context" / "project" / "prohibited.yaml"
    data = yaml.safe_load(path.read_text())
    data["content"]["prohibitions"] = [
        {"id": "PP-001", "kind": "practice",
         "subject": "real patient data in portal development or test environments",
         "instead": "synthetic patient data"}]
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    _intake(env, repo, "portal", {
        "project": "{name: portal, purpose: patients view their records and appointments, "
                   "technology: [web, mobile]}",
        "data": "[PHI, PII]",
        "answers": '{id: q-ai-use-1, question: "How will the team use AI tools?", answer: '
                   '"Developers use the approved AI assistant to draft the portal\'s code and '
                   'tests.", answered_by: Pat Lee <pat@acme-health.org>}'})
    return {"repo": repo, "project": "portal", "conflict": "NO-003", "cite": None,
            "findings_in": "projects/portal"}


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
    # The one owner role is held (D-92), so versioning is not refused for it.
    run(env, repo / "domain", "scs", "intake", "set", "owners", "{role: owner, person: Pat Lee}")
    run(env, repo, "scs", "intake", "record-finding", "--workspace", "domain", "--id", "rf-1",
        "--kind", "missing-protection", "--target", "scd:project:prohibited#NO-001",
        "--finding", "No approved alternative is named for personal AI accounts",
        "--decision", "deferred", "--decided-by", APPROVER)
    return {"repo": repo, "deferred": "rf-1", "deferred_words": ["alternative", "rf-1"]}


def unowned(work: Path, env: dict) -> dict:
    """A drafted, reviewed Domain whose section owner is not yet named (release-owners): since
    ISS-056 the owner and the releaser are asked at release."""
    repo = _domain(work, env)
    _prohibitions(repo, GOOD)
    _intake(env, repo, "domain", {
        **DOMAIN_INTAKE,
        "answers": '{id: q-people-1, question: "Who is involved?", answer: "Pat Lee, Quality '
                   'Manager; Sam Ortiz, CTO.", answered_by: Pat Lee <pat@acme-health.org>}'})
    commit(env, repo)
    return {"repo": repo}


def placeholder(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD, created_by="Developer <dev@example.com>")
    return {"repo": repo}


def versioned(work: Path, env: dict) -> dict:
    repo = _domain(work, env)
    _prohibitions(repo, GOOD)
    _release(env, repo)
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


BUILDERS = {f.__name__: f for f in (empty, resume, unreleased, released, draft_doc, invalid,
                                     ready, unowned, placeholder, versioned, review, project_review)}
