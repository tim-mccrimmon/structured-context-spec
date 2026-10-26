"""
New command - scaffolds a Domain repository (`scs new domain`) and the Project workspaces in it
(`scs new project`) (RFC 0002 section 9)
"""

import re
import shutil
import tempfile
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import List

import click
from scs_validator.envelope import SCS_VERSION, Change, relative
from scs_validator.names import reserved_bundle_name
from scs_validator.workspace import CONFIG, read_config

from scs_tools import git, identity
from scs_tools.machine import EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.utils.files import (
    copy_template,
    create_directory_structure,
    get_template_path,
    write_file,
)
from scs_tools.utils.project_types import (
    ONTOLOGY_MODELS,
    get_concept_info,
    get_ontology_model_config,
)
from scs_tools.workspace import find_domain_repository

# The meta bundle published with the spec (meta/ at the repo root). scs-validator ships a copy,
# so a Domain bundle's import of it resolves without the bundle being in the workspace. Kept at
# 0.6.0 for SCS 0.7 (D-21).
META_BUNDLE_REF = "bundle:meta:0.6.0"

# Concepts every Domain bundle gets, whatever its ontology model: facts about the organization
# and its binary prohibitions. Concept id -> (name, description, SCD names). Templates live in
# templates/bundles/concepts/common/ and templates/scds/common/. The personal ontology gets only
# the prohibited concept (boundaries), in a Domain or a Project (D-62, D-72); identity is
# provenance, not a concept (D-63).
DOMAIN_COMMON_CONCEPTS = {
    "company": (
        "Company",
        "Facts about the organization that every agent should know",
        ["company-profile"],
    ),
    "prohibited": (
        "Prohibited Tools and Practices",
        "Tools and practices forbidden, without exception, in all of the organization's work",
        ["prohibited"],
    ),
}
PERSONAL_CONCEPTS = ["prohibited"]

# A workspace name becomes a directory, a bundle id (`bundle:<name>`), and a tag prefix.
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _template_model(concept: str, ontology: str) -> str:
    """Template directory for a concept: `common` for the Domain-wide concepts."""
    return "common" if concept in DOMAIN_COMMON_CONCEPTS else ontology


def _scs_tools_version() -> str:
    """The installed scs-tools package version, or "unknown" if it can't be read. Read from
    package metadata rather than hardcoding a version string, which goes stale the moment
    the package is re-versioned (see the matching fix in commands/bundle.py)."""
    try:
        return pkg_version("scs-tools")
    except PackageNotFoundError:
        return "unknown"


@click.group()
def new():
    """
    Create a Domain repository or a Project workspace in one

    `scs new domain` creates an organization's Domain repository, `<name>-context/`, with the
    Domain workspace (governance that applies to all work) under `domain/`. `scs new project`,
    run inside that repository, adds a Project workspace under `projects/`. The two bundles are
    independent: neither imports the other.
    """
    pass


def _workspace_options(f):
    """Options shared by `scs new domain` and `scs new project`."""
    for option in reversed(_WORKSPACE_OPTIONS):
        f = option(f)
    return f


_WORKSPACE_OPTIONS = [
    click.argument("name", required=False),
    click.option(
        "--ontology",
        type=click.Choice(list(ONTOLOGY_MODELS.keys())),
        default=None,
        help="Ontology model to scaffold against (a Domain: default sdlc; a Project: default "
        "its Domain's). Each supplies one template set for a Domain and one for a Project; "
        "remove what does not apply. personal supplies only boundaries (the prohibited "
        "concept).",
    ),
    click.option("--author", default=None, help="Author name for provenance"),
    click.option("--email", default=None, help="Author email for provenance"),
    click.option("--interactive", "-i", is_flag=True, help="Interactive mode with prompts"),
    click.option(
        "--no-interactive",
        is_flag=True,
        help="Disable interactive mode (use defaults/flags only)",
    ),
    click.option("--dry-run", is_flag=True, help="Report what would be created; write nothing"),
]


@new.command()
@_workspace_options
@click.option(
    "--dir",
    "directory",
    type=click.Path(),
    default=None,
    help="Directory to create the repository in (default: current directory)",
)
@machine_command("new domain")
def domain(
    envelope: Envelope,
    out: Output,
    name,
    ontology,
    author,
    email,
    interactive,
    no_interactive,
    dry_run,
    directory,
):
    """
    Create a Domain repository for an organization or a person

    Creates `NAME-context/`, a git repository holding the Domain workspace under `domain/` and,
    later, one workspace per Project under `projects/`. The Domain bundle holds the governance
    that applies to all of the owner's work. The repository also gets AGENTS.md (with a
    CLAUDE.md pointer), a CI workflow that runs `scs-validate --strict`, and an initial commit.

    Ontology models: sdlc (default), mca, cdmo, personal. The scaffold supplies the
    ontology's Domain templates; remove what does not apply. A personal Domain gets only
    boundaries (the prohibited concept); its other concepts are defined with the user.

    \b
    Examples:
        scs new domain acme-health                 # Interactive mode (default)
        scs new domain acme-funding --ontology mca
        scs new domain jdoe --ontology personal
        scs new domain acme --author "Jane Doe" --email "jane@acme-health.org" --no-interactive

    See also: scs new project
    """
    name, author, email = _ask("domain", out, name, author, email, interactive, no_interactive)
    _check_name(name, "domain")
    ontology = ontology or "sdlc"
    parent = Path(directory) if directory else Path.cwd()
    repo = parent / f"{name}-context"
    if repo.exists():
        raise CommandError("WORKSPACE_EXISTS", f"'{repo}' already exists")
    if not git.available():
        raise CommandError("GIT_REQUIRED", "scs new domain needs git, and git was not found")
    envelope.result = {"repository": str(repo), "workspace": "domain", "bundle": f"bundle:{name}"}
    if dry_run:
        with tempfile.TemporaryDirectory(prefix="scs-new-") as tmp:
            target = Path(tmp) / repo.name
            _scaffold(
                Output(True), target, target / "domain", "domain", name, ontology, author, email
            )
            _create_repository_files(target, name)
            shown = [relative(p, target) for p in _files(target)]
        envelope.changes.extend(Change("create", path=p) for p in shown)
        envelope.changes.append(Change("git-init", ref="main"))
        paths = [{"path": p, "status": "A"} for p in sorted(shown)]
        envelope.changes.append(Change("git-commit", ref="HEAD", paths=paths))
        out.echo(f"Would create Domain repository {repo} ({len(shown)} files) and commit it")
        return

    out.echo(f"Creating SCS Domain repository: {repo.name}")
    out.echo(f"Location: {repo}\n")
    try:
        _scaffold(
            out,
            repo,
            repo / "domain",
            "domain",
            name,
            ontology,
            author,
            email,
        )
        _create_repository_files(repo, name)
        written = _files(repo)
        git.run(repo, "init", "-q", "--initial-branch=main")
        git.run(repo, "add", "-A")
        message = f"Create Domain repository {repo.name} (scs new domain)"
        git.run(repo, "commit", "-q", "-m", message)
        committed = git.committed_paths(repo)
    except git.GitError as e:
        shutil.rmtree(repo, ignore_errors=True)
        raise CommandError("GIT_COMMAND_FAILED", str(e))
    except BaseException:
        shutil.rmtree(repo, ignore_errors=True)
        raise

    envelope.changes.extend(Change("create", path=relative(p, repo)) for p in written)
    envelope.changes.append(Change("git-init", ref="main"))
    envelope.changes.append(Change("git-commit", ref="HEAD", paths=committed))

    out.echo(f"\n✓ Domain repository '{repo.name}' created, with an initial commit.")
    out.echo("\nNext steps:")
    out.echo(f"  cd {repo.name}")
    out.echo("  # Write directives, prohibitions, and facts in domain/context/project/")
    out.echo("  scs new project <name>          # add a Project workspace")
    out.echo("  scs-validate --strict           # validate every workspace")
    out.echo("  scs compile domain/bundles/domain-bundle.yaml --allow-draft")


@new.command()
@_workspace_options
@click.option(
    "--dir",
    "directory",
    type=click.Path(),
    default=None,
    help="The Domain repository to add the Project to (default: the one containing the "
    "current directory)",
)
@machine_command("new project")
def project(
    envelope: Envelope,
    out: Output,
    name,
    ontology,
    author,
    email,
    interactive,
    no_interactive,
    dry_run,
    directory,
):
    """
    Create a Project workspace in a Domain repository

    Adds `projects/NAME/` to the Domain repository containing the current directory (or the
    one given with --dir). The Project bundle holds the governance for one project. It imports
    its concept bundles directly and does not import the Domain bundle; a runtime applies the
    two side by side. Create the repository first with `scs new domain`.

    By default, prompts for missing required information interactively.
    Use --no-interactive to disable prompts and require all flags.

    Ontology models: sdlc, mca, cdmo, personal; by default, the Domain's. The scaffold
    supplies the ontology's Project templates; remove what does not apply.

    \b
    Examples:
        scs new project                           # Interactive mode (default)
        scs new project medication-adherence      # Interactive for missing fields
        scs new project my-funder --ontology mca  # Merchant Cash Advance ontology
        scs new project my-app --author "Jane Doe" --email "jane@acme-health.org" --no-interactive

    See also: scs new domain, scs init (for adding SCS to existing projects)
    """
    start = (Path(directory) if directory else Path.cwd()).resolve()
    repo = find_domain_repository(start)
    if repo is None:
        raise CommandError(
            "DOMAIN_WORKSPACE_MISSING",
            f"No Domain repository at or above {start}. A Project workspace lives in one: "
            "create it with 'scs new domain NAME', then run 'scs new project' inside it.",
        )
    name, author, email = _ask("project", out, name, author, email, interactive, no_interactive)
    _check_name(name, "project")
    ontology = ontology or _domain_ontology(repo)
    workspace = repo / "projects" / name
    if workspace.exists():
        shown = relative(workspace, repo)
        raise CommandError("WORKSPACE_EXISTS", f"'{shown}' already exists", path=shown)
    envelope.result = {"repository": str(repo), "workspace": name, "bundle": f"bundle:{name}"}
    if dry_run:
        with tempfile.TemporaryDirectory(prefix="scs-new-") as tmp:
            target = Path(tmp) / repo.name
            staged = target / "projects" / name
            _scaffold(Output(True), target, staged, "project", name, ontology, author, email)
            files = [relative(p, target) for p in _files(staged)]
        envelope.changes.extend(Change("create", path=p) for p in files)
        out.echo(f"Would create Project {relative(workspace, repo)} ({len(files)} files)")
        return

    out.echo(f"Creating SCS project: {name}")
    out.echo(f"Location: {workspace}\n")
    try:
        _scaffold(out, repo, workspace, "project", name, ontology, author, email)
    except BaseException:
        shutil.rmtree(workspace, ignore_errors=True)
        raise

    envelope.changes.extend(Change("create", path=relative(p, repo)) for p in _files(workspace))

    out.echo(f"\n✓ Project '{name}' created in {relative(workspace, repo)}.")
    out.echo("\nNext steps:")
    out.echo(
        "  # Write directives, prohibitions, and facts in "
        f"{relative(workspace, repo)}/context/project/"
    )
    out.echo("  scs-validate --strict           # at the repository root")
    out.echo(f"  scs compile {relative(workspace, repo)}/bundles/project-bundle.yaml --allow-draft")


def _domain_ontology(repo: Path) -> str:
    """The Domain workspace's ontology, which a new Project inherits (D-74); sdlc if unset."""
    try:
        config = read_config(repo / "domain" / CONFIG)
    except ValueError:
        config = {}
    value = config.get("ontology") or config.get("ontology_model")
    return value if value in ONTOLOGY_MODELS else "sdlc"


def _check_name(name: str, kind: str) -> None:
    """Refuse a name that cannot be a directory, a bundle id, and a tag prefix, or that is
    reserved (D-33)."""
    if not NAME_RE.match(name):
        raise CommandError(
            "WORKSPACE_NAME_INVALID",
            f"'{name}' is not a valid {kind} name: use letters, digits, '.', '_', and '-', "
            "starting with a letter or digit",
            exit_code=EXIT_USAGE,
        )
    if kind == "project" and name == "domain":
        raise CommandError(
            "WORKSPACE_NAME_INVALID",
            "A Project cannot be named 'domain': that is the Domain workspace's name, and the "
            "two would share version tags",
            exit_code=EXIT_USAGE,
        )
    concepts = {c for m in ONTOLOGY_MODELS.values() for c in m["concepts"]}
    if name in DOMAIN_COMMON_CONCEPTS or name in concepts:
        raise CommandError(
            "WORKSPACE_NAME_INVALID",
            f"'{name}' is the name of a concept bundle, so the {kind} bundle's id "
            f"(bundle:{name}) would collide with it; choose another name",
            exit_code=EXIT_USAGE,
        )
    reserved = reserved_bundle_name(f"bundle:{name}")
    if reserved:
        raise CommandError(
            "RESERVED_BUNDLE_NAME",
            f"'{reserved}' is reserved for a later SCS release (plan, test-plan, qa); "
            f"choose another {kind} name",
        )


def _ask(kind, out, name, author, email, interactive, no_interactive):
    """Fill in missing values by prompting in interactive human mode; otherwise they are
    required (NO_INPUT). Machine mode never prompts."""
    label = kind.capitalize()
    should_prompt = (not no_interactive or interactive) and not out.machine
    if should_prompt:
        if not name:
            click.echo(f"=== SCS {label} Setup ===\n")
            name = click.prompt(f"{label} name", type=str)
    elif not name:
        message = f"{label} name is required in non-interactive mode"
        raise CommandError("NO_INPUT", message, exit_code=EXIT_USAGE)
    # Never invented: prompted with git's values as defaults, else required (D-13, D-71)
    author, email = identity.author(author, email, prompt=should_prompt)
    if should_prompt:
        click.echo()
    return name, author, email


def _files(root: Path) -> List[Path]:
    """Every file under `root`, outside `.git/`, in path order."""
    return sorted(
        p for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts
    )


def _create_repository_files(repo: Path, name: str) -> None:
    """AGENTS.md and its CLAUDE.md pointer (D-31), the CI workflow, .gitignore (D-59),
    .gitattributes, and projects/."""
    templates = get_template_path() / "repository"
    major, minor = SCS_VERSION.split(".")[:2]
    variables = {
        "repo_name": repo.name,
        "domain_name": name,
        "tools_version": _scs_tools_version(),
        # Repository mode and the 0.7 checks start with the validator for this spec version.
        "validator_requirement": f"scs-validator>={SCS_VERSION},<{major}.{int(minor) + 1}",
    }
    copy_template(templates / "AGENTS.md", repo / "AGENTS.md", variables)
    copy_template(templates / "CLAUDE.md", repo / "CLAUDE.md", variables)
    copy_template(
        templates / "scs-validate.yml",
        repo / ".github" / "workflows" / "scs-validate.yml",
        variables,
    )
    copy_template(templates / "gitignore", repo / ".gitignore")
    copy_template(templates / "gitattributes", repo / ".gitattributes")
    # git does not track empty directories; keep projects/ in the initial commit
    write_file(repo / "projects" / ".gitkeep", "")


def _scaffold(out, repo, base_path, kind, name, ontology, author, email):
    """Create a `kind` ("domain" or "project") workspace at `base_path` in Domain repository
    `repo`. Its bundle is `bundle:<name>`. The templates depend on the ontology and the
    workspace kind only (D-64): the ontology's full set for that kind."""
    out.echo(f"Ontology model: {ontology}")

    model_config = get_ontology_model_config(ontology)
    # No SCD is left out: the user (or the agent with the user) removes what does not apply.
    config: dict = {"exclude_scds": []}
    concepts = list(model_config["concepts"])
    if kind == "domain" and ontology == "sdlc":
        # The Global profile: only concepts with organization-wide SCDs
        concepts = [c for c in concepts if c in _sdlc_domain_scd_mapping()]
    elif kind == "domain" and "domain_scds" in model_config:
        concepts = [c for c in concepts if c in model_config["domain_scds"]]
    ontology_concepts = list(concepts)
    if ontology == "personal":
        concepts = list(PERSONAL_CONCEPTS)
    elif kind == "domain":
        concepts = [*DOMAIN_COMMON_CONCEPTS, *concepts]

    out.echo("Creating directory structure...")
    create_directory_structure(base_path, name)

    variables = {
        "bundle_kind": kind,
        "meta_bundle_ref": META_BUNDLE_REF,
        "project_name": name,
        "ontology": ontology,
        "domain_id": model_config["domain"],
        "domain_name": model_config["domain_name"],
        "repo_name": repo.name,
        "workspace_dir": relative(base_path, repo),
        "author": author,
        "email": email,
        # Provenance identifies a person as `Name <email>` (D-28, D-63)
        "created_by": f"{author} <{email}>",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "concepts": concepts,
        "config": config,
    }

    out.echo("Creating bundle files...")
    _create_bundles(base_path, kind, concepts, variables, ontology, out)

    out.echo("Creating Domain Ontology manifest...")
    _create_domain_manifest(base_path, concepts, variables, model_config)

    out.echo("Creating SCD files...")
    created = _create_scds(base_path, kind, concepts, variables, config, ontology)
    if kind == "domain":
        # Concept bundle templates list the project profile's SCDs; list what was generated
        for concept, scd_names in created.items():
            _set_concept_scds(base_path / "bundles" / "concepts" / f"{concept}.yaml", scd_names)

    # Concept documentation templates are not yet built for non-sdlc ontology models
    if ontology == "sdlc":
        out.echo("Creating concept documentation templates...")
        _create_concept_docs(base_path, ontology_concepts, variables, out)

    out.echo("Creating supporting files...")
    _create_supporting_files(base_path, variables)


def _create_domain_manifest(base_path: Path, concepts: list, variables: dict, model_config: dict):
    """Create ontology/domain-manifest.yaml (D-04): the Domain Ontology of the generated concepts,
    including relationships when the ontology model defines them (e.g. mca; sdlc has none,
    deliberately flat)."""
    manifest_template = get_template_path() / "domain" / "domain-manifest.yaml"
    info_map = {
        **model_config["concept_info"],
        **{c: (name, desc) for c, (name, desc, _) in DOMAIN_COMMON_CONCEPTS.items()},
    }
    # A profile may leave concepts out; drop relationships to them so the manifest resolves
    present = {f"concept:{c}" for c in concepts}
    relationships = {
        c: [rel for rel in rels if rel["target"] in present]
        for c, rels in model_config["relationships"].items()
    }
    concept_info = get_concept_info(
        concepts, info_map, relationships, model_config.get("satisfies")
    )
    copy_template(
        manifest_template,
        base_path / "ontology" / "domain-manifest.yaml",
        {**variables, "concept_info": concept_info},
    )


def _create_bundles(
    base_path: Path, kind: str, concepts: list, variables: dict, ontology: str, out: Output
):
    """Create the root bundle (domain or project) and its concept bundles (SCS 0.6.0).
    The meta bundle is not scaffolded: a Domain bundle imports the published one."""
    template_path = get_template_path() / "bundles"

    copy_template(
        template_path / f"{kind}-bundle.yaml",
        base_path / "bundles" / f"{kind}-bundle.yaml",
        variables,
    )

    # Create concept bundles (the ontology model's functional areas)
    for concept in concepts:
        concept_template = (
            template_path / "concepts" / _template_model(concept, ontology) / f"{concept}.yaml"
        )
        if concept_template.exists():
            copy_template(
                concept_template,
                base_path / "bundles" / "concepts" / f"{concept}.yaml",
                variables,
            )
        else:
            out.echo(f"Warning: Template for concept '{concept}' not found, skipping...")


def _create_scds(
    base_path: Path, kind: str, concepts: list, variables: dict, config: dict, ontology: str
) -> dict:
    """Create SCD YAML files. Returns the SCD names created, per concept."""
    templates_root = get_template_path() / "scds"
    model_config = get_ontology_model_config(ontology)

    if "scds" in model_config:
        scd_mapping = dict(model_config["domain_scds" if kind == "domain" else "scds"])
    elif ontology != "sdlc":
        # Other ontology models map one SCD per concept (concept id == scd id) - see
        # e.g. examples/merchant-cash-advance/concepts/*.yaml, which each import exactly the
        # SCD of the same name.
        scd_mapping = {concept: [concept] for concept in concepts}
    elif kind == "domain":
        scd_mapping = _sdlc_domain_scd_mapping()
    else:
        scd_mapping = _sdlc_scd_mapping()
    scd_mapping.update({c: scds for c, (_, _, scds) in DOMAIN_COMMON_CONCEPTS.items()})

    # Get excluded SCDs from config
    exclude_scds = config.get("exclude_scds", [])

    created = []
    by_concept: dict = {}
    for concept in concepts:
        scds = scd_mapping.get(concept, [])
        for scd_name in scds:
            # Skip excluded SCDs
            if scd_name in exclude_scds:
                continue

            scd_template = templates_root / _template_model(concept, ontology) / f"{scd_name}.yaml"
            if scd_template.exists():
                dest = base_path / "context" / "project" / f"{scd_name}.yaml"
                copy_template(scd_template, dest, variables)
                created.append(dest)
                by_concept.setdefault(concept, []).append(scd_name)

    generated = {f"scd:project:{path.stem}" for path in created}
    for path in created:
        _drop_dangling_relationships(path, generated)
    return by_concept


def _set_concept_scds(bundle_path: Path, scd_names: list):
    """Replace the `scds:` list of a scaffolded concept bundle with `scd_names`."""
    if not bundle_path.is_file():
        return
    lines = bundle_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.rstrip() == "scds:") + 1
    end = start
    while end < len(lines) and (not lines[end].strip() or lines[end].lstrip().startswith("- scd:")):
        end += 1
    listed = [f"  - scd:project:{name}\n" for name in scd_names]
    bundle_path.write_text("".join(lines[:start] + listed + ["\n"] + lines[end:]), encoding="utf-8")


def _drop_dangling_relationships(scd_path: Path, generated: set):
    """Remove relationships whose target is a project SCD this scaffold did not generate
    (e.g. hipaa-compliance in a non-healthcare project). Works on the text so the template's
    comments survive; relationship items are `  - type:` lines with 4-space continuations."""
    lines = scd_path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    item: list[str] = []
    kept, in_block = 0, False

    def flush():
        nonlocal item, kept
        target = next(
            (ln.split(":", 1)[1].strip().strip('"') for ln in item if "target:" in ln), ""
        )
        if not (target.startswith("scd:project:") and target not in generated):
            out.extend(item)
            kept += 1
        item = []

    for line in lines:
        if line.startswith("relationships:"):
            in_block, block_start = True, len(out)
            out.append(line)
            continue
        if in_block and line.startswith("  - type:"):
            if item:
                flush()
            item = [line]
        elif in_block and item and line.startswith("    "):
            item.append(line)
        else:
            if item:
                flush()
            if in_block and line.strip() and not line.startswith(" "):
                in_block = False
            out.append(line)
    if item:
        flush()
    if not kept and any(ln.startswith("relationships:") for ln in out):
        out[block_start] = "relationships: []\n"
    scd_path.write_text("".join(out), encoding="utf-8")


def _sdlc_scd_mapping() -> dict:
    """SCD names per concept, for the sdlc ontology model only."""
    return {
        "business-context": [
            "problem-definition",
            "stakeholders",
            "business-objectives",
            "opportunity-analysis",
            "constraints-and-assumptions",
            "success-criteria",
        ],
        "architecture": [
            "system-context",
            "tech-stack",
            "integration-map",
            "component-model",
        ],
        "security": [
            "authn-authz",
            "data-protection",
            "data-handling",
            "threat-model",
        ],
        "performance-reliability": [
            "response-time",
            "availability",
            "fault-tolerance",
            "scalability",
        ],
        "usability-accessibility": [
            "ux-principles",
            "accessibility-compliance",
            "error-handling-ux",
        ],
        "compliance-governance": [
            "soc2-controls",
            "hipaa-compliance",
            "chai-adherence",
            "tefca-participation",
        ],
        "data-provenance": [
            "data-model",
            "provenance-tracking",
            "retention-policy",
        ],
        "testing-validation": [
            "test-coverage",
            "validation-plan",
            "qa-procedures",
        ],
        "deployment-operations": [
            "infrastructure-definition",
            "observability",
            "incident-response",
        ],
        "safety-risk": [
            "risk-assessment",
            "safety-checklist",
        ],
        "ethics-ai-accountability": [
            "ai-usage-policy",
            "audit-trail",
            "model-bias",
        ],
    }


def _sdlc_domain_scd_mapping() -> dict:
    """The sdlc Global profile: SCD names per concept for a Domain bundle. Only SCDs that
    state organization-wide policy or standards; SCDs that describe one system (problem
    definition, system context, threat model, performance targets, risk register, ...)
    belong to Project bundles."""
    return {
        "architecture": ["tech-stack", "integration-map"],
        "security": ["authn-authz", "data-protection", "data-handling"],
        "usability-accessibility": ["ux-principles", "accessibility-compliance"],
        "compliance-governance": [
            "soc2-controls",
            "hipaa-compliance",
            "chai-adherence",
            "tefca-participation",
            "audit-requirements",
            "policy-enforcement",
        ],
        "data-provenance": ["provenance-tracking", "retention-policy"],
        "testing-validation": ["test-coverage", "qa-procedures", "engineering-practices"],
        "deployment-operations": [
            "infrastructure-definition",
            "observability",
            "incident-response",
        ],
        "ethics-ai-accountability": ["ai-usage-policy", "audit-trail", "model-bias"],
    }


def _create_concept_docs(base_path: Path, concepts: list, variables: dict, out: Output):
    """Create concept documentation markdown templates for users to fill in"""
    import shutil

    template_path = get_template_path() / "docs"

    for concept in concepts:
        concept_template_dir = template_path / concept
        if concept_template_dir.exists():
            # Find the template markdown file in this concept directory
            template_files = list(concept_template_dir.glob("*-template.md"))
            if template_files:
                template_file = template_files[0]
                # Destination: docs/{concept}/{concept}-brief.md
                dest_file = template_file.name.replace("-template", "")
                dest_path = base_path / "docs" / concept / dest_file

                # Create parent directory if it doesn't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file directly without Jinja2 rendering (these are user templates)
                shutil.copy2(template_file, dest_path)
        else:
            out.echo(f"Warning: Concept docs template for {concept} not found, skipping...")


def _create_supporting_files(base_path: Path, variables: dict):
    """Create README, docs/GETTING_STARTED.md, and .scs/config. Repository-wide files
    (.gitignore, .gitattributes) are created once, at the Domain repository root."""
    template_path = get_template_path()

    copy_template(template_path / "project-README.md", base_path / "README.md", variables)
    copy_template(
        template_path / "GETTING_STARTED.md",
        base_path / "docs" / "GETTING_STARTED.md",
        variables,
    )

    # .scs/config (D-06): name is the workspace name, `domain` or the Project's directory name
    # (D-03); scs_version is the spec version.
    kind = variables["bundle_kind"]
    lines = [
        "# SCS Workspace Configuration",
        f"bundle_type: {kind}",
        f"name: {'domain' if kind == 'domain' else variables['project_name']}",
        f"ontology: {variables['ontology']}",
    ]
    lines += [f"scs_version: {SCS_VERSION}", f"tools_version: {_scs_tools_version()}"]
    write_file(base_path / ".scs" / "config", "\n".join(lines) + "\n")
