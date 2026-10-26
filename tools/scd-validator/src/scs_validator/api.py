"""In-process validation API (D-37).

`scs-validate` and `scs-tools` call these functions instead of running the validator as a
subprocess. Each returns a `Report`; nothing here prints or exits.

    from scs_validator import api
    report = api.validate_bundle("bundles/project-bundle.yaml")
    report.exit_code(strict=True)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union

from .bundle_validator import BundleValidator
from .checks import CheckContext, run_checks
from .completeness_validator import CompletenessValidator
from .ontology_validator import OntologyValidator
from .parser import Parser
from .relationship_validator import RelationshipValidator
from .resolver import BundleTree, Index, resolve
from .rules_loader import RulesLoader
from .schema_validator import SchemaValidator
from .semantic_validator import SemanticValidator
from .utils import ValidationError, ValidationResult, resolve_schema_dir
from .workspace import Workspace, discover_workspaces, is_repository

PathLike = Union[str, Path]
Log = Callable[[str], None]


class SchemaDirNotFound(Exception):
    """No JSON Schema directory was found (exit code 4)."""

    def __init__(self, searched: List[Path]):
        self.searched = searched
        super().__init__("Schema directory not found")


@dataclass
class WorkspaceReport:
    name: str
    path: Path
    results: List[ValidationResult] = field(default_factory=list)


@dataclass
class Report:
    """Results of one run. In repository mode, `results` holds repository-level findings and
    `workspaces` one report per workspace."""

    results: List[ValidationResult] = field(default_factory=list)
    workspaces: List[WorkspaceReport] = field(default_factory=list)
    repository: Optional[Path] = None

    def all_results(self) -> List[ValidationResult]:
        return self.results + [r for w in self.workspaces for r in w.results]

    def exit_code(self, strict: bool = False) -> int:
        return exit_code(self.all_results(), strict)


def exit_code(results: Iterable[ValidationResult], strict: bool) -> int:
    """1 on errors; 2 on warnings under --strict; otherwise 0. Info never counts (D-10)."""
    results = list(results)
    if any(not r.passed for r in results):
        return 1
    if strict and any(r.warning_count > 0 for r in results):
        return 2
    return 0


class Validators:
    """The validators of one run, sharing a schema directory and rules."""

    def __init__(
        self, schema_dir: Optional[PathLike] = None, completeness_rules: Optional[PathLike] = None
    ):
        schema_path, searched = resolve_schema_dir(str(schema_dir) if schema_dir else None)
        if schema_path is None or not schema_path.exists():
            raise SchemaDirNotFound(searched if searched else [Path(str(schema_path))])
        self.schema_dir = schema_path
        rules = RulesLoader()
        self.parser = Parser()
        self.schema = SchemaValidator(schema_path)
        self.semantic = SemanticValidator(rules)
        self.bundle = BundleValidator(rules)
        self.relationship = RelationshipValidator(rules)
        self.ontology = OntologyValidator(rules)
        self.completeness = CompletenessValidator(
            rules, Path(completeness_rules) if completeness_rules else None
        )


def _quiet(_: str) -> None:
    pass


def validate_files(
    paths: Iterable[PathLike],
    *,
    schema_dir: Optional[PathLike] = None,
    validators: Optional[Validators] = None,
    log: Log = _quiet,
) -> Report:
    """Validate individual SCD files."""
    v = validators or Validators(schema_dir)
    syntax_result = ValidationResult("syntax")
    schema_result = ValidationResult("schema")
    semantic_result = ValidationResult("semantic")
    files_checked = 0

    for path in map(Path, paths):
        log(f"Validating {path}...")
        try:
            scd = v.parser.load_scd(path)
            files_checked += 1
            schema_result.extend(v.schema.validate_scd(scd, str(path)))
            semantic_result.extend(v.semantic.validate_scd(scd, str(path)))
        except ValidationError as e:
            syntax_result.add_error(e)

    for result in (syntax_result, schema_result, semantic_result):
        result.details["files_checked"] = files_checked
    return Report([syntax_result, schema_result, semantic_result])


def validate_domain_manifest(
    path: PathLike,
    *,
    schema_dir: Optional[PathLike] = None,
    validators: Optional[Validators] = None,
    log: Log = _quiet,
) -> Report:
    """Validate a domain manifest: schema, then Domain Ontology rules (RFC-0001).

    Only the manifest itself is validated - SCDs and concept bundles aren't loaded here, so
    Domain Ontology rules 6 and 7 (which need that broader context) are skipped.
    """
    v = validators or Validators(schema_dir)
    syntax_result = ValidationResult("syntax")
    schema_result = ValidationResult("domain_manifest_schema")
    ontology_result = ValidationResult("ontology")
    log(f"Validating domain manifest {path}...")
    try:
        manifest = v.parser.load_domain_manifest(Path(path))
        schema_result = v.schema.validate_domain_manifest(manifest, str(path))
        # Ontology rules run even when the schema fails: concern residue (rule 8) is useful
        # even then (a legacy 'concerns' field triggers both a schema error and rule 8).
        ontology_result = v.ontology.validate_domain_manifest(manifest, str(path))
    except ValidationError as e:
        syntax_result.add_error(e)
    return Report([syntax_result, schema_result, ontology_result])


def validate_checkpoint(
    path: PathLike,
    *,
    schema_dir: Optional[PathLike] = None,
    validators: Optional[Validators] = None,
    log: Log = _quiet,
) -> Report:
    """Validate a checkpoint record: schema only (any-ai-actor-model.md, RFC-0001/ISS-006)."""
    v = validators or Validators(schema_dir)
    syntax_result = ValidationResult("syntax")
    schema_result = ValidationResult("checkpoint_record_schema")
    log(f"Validating checkpoint record {path}...")
    try:
        record = v.parser.load_checkpoint_record(Path(path))
        schema_result = v.schema.validate_checkpoint_record(record, str(path))
    except ValidationError as e:
        syntax_result.add_error(e)
    return Report([syntax_result, schema_result])


def _bundle_results(
    bundle_path: Path, v: Validators, skip_completeness: bool, log: Log
) -> tuple[List[ValidationResult], Optional[BundleTree]]:
    """The bundle pipeline (levels 1-6) for one bundle, and its resolved tree."""
    syntax_result = ValidationResult("syntax")
    bundle_schema_result = ValidationResult("bundle_schema")
    semantic_result = ValidationResult("semantic")
    bundle_result = ValidationResult("bundle")
    relationship_result = ValidationResult("relationships")
    completeness_result = ValidationResult("completeness")
    tree: Optional[BundleTree] = None

    log(f"Validating bundle {bundle_path}...")
    try:
        # Level 1: parse
        bundle = v.parser.load_bundle(bundle_path)
        bundle_type = bundle.get("type", "unknown")
        log(f"Bundle ID: {bundle.get('id', 'unknown')}")
        log(f"Bundle Type: {bundle_type}")

        # Level 2: bundle schema
        bundle_schema_result = v.schema.validate_bundle(bundle, str(bundle_path))
        if not bundle_schema_result.passed:
            # Stop here (SCD loading, relationships, completeness all assume a well-formed
            # bundle), but still run the Level 5 type check: it can add a clearer message on
            # top of the generic schema error (e.g. RFC-0001 rule 8's hint for 'concern').
            bundle_result = v.bundle.validate_bundle(bundle, str(bundle_path))
            results = [syntax_result, bundle_schema_result]
            if bundle_result.errors or bundle_result.warnings:
                results.append(bundle_result)
            return results, None

        # Level 5: bundle organization (XOR constraint, type rules)
        bundle_result = v.bundle.validate_bundle(bundle, str(bundle_path))

        # Any bundle type can be the root: Domain and Project bundles are independent trees.
        tree = resolve(bundle_path)
        bundle_result.extend(v.bundle.validate_tree(tree))
        bundle_result.extend(v.bundle.validate_digests(tree))
        log(f"Resolved {len(tree.bundles) - 1} imported bundles, {len(tree.scds)} SCDs")

        all_scds = []
        for resolved_scd in tree.scds:
            try:
                scd_data = v.parser.load_scd(resolved_scd.path)
            except Exception as e:
                log(f"  Warning: Could not load {resolved_scd.path}: {e}")
                continue
            all_scds.append(scd_data)
            # Level 3: semantic
            semantic_result.extend(v.semantic.validate_scd(scd_data, str(resolved_scd.path)))
        log(f"Successfully loaded {len(all_scds)} SCDs")

        # Level 4: relationships
        if all_scds:
            relationship_result = v.relationship.validate_relationships(
                all_scds, bundle_type, str(bundle_path)
            )

        # Level 6: completeness
        if not skip_completeness and bundle_type in ("project", "domain"):
            completeness_result = v.completeness.validate_completeness(
                bundle, all_scds, str(bundle_path), tree.project_root, tree=tree
            )
        elif skip_completeness:
            log("Skipping completeness validation (--skip-completeness)")

    except ValidationError as e:
        syntax_result.add_error(e)

    results = [syntax_result, bundle_schema_result, semantic_result, bundle_result]
    if relationship_result.errors or relationship_result.warnings:
        results.append(relationship_result)
    if not skip_completeness and (completeness_result.errors or completeness_result.warnings):
        results.append(completeness_result)
    return results, tree


def validate_bundle(
    path: PathLike,
    *,
    schema_dir: Optional[PathLike] = None,
    completeness_rules: Optional[PathLike] = None,
    skip_completeness: bool = False,
    strict: bool = False,
    validators: Optional[Validators] = None,
    log: Log = _quiet,
) -> Report:
    """Validate a bundle, its import tree, and the workspace checks for its project root."""
    v = validators or Validators(schema_dir, completeness_rules)
    bundle_path = Path(path)
    results, tree = _bundle_results(bundle_path, v, skip_completeness, log)
    if tree is not None:
        context = CheckContext(
            workspace_root=tree.project_root,
            index=Index([tree.project_root]),
            trees=[tree],
            schema_dir=v.schema_dir,
            strict=strict,
        )
        results.extend(run_checks(context))
    return Report(results)


def _validate_workspace(
    workspace: Workspace, v: Validators, skip_completeness: bool, strict: bool, log: Log
) -> WorkspaceReport:
    report = WorkspaceReport(workspace.name, workspace.root)
    trees = []
    for bundle_path in workspace.root_bundles():
        results, tree = _bundle_results(bundle_path, v, skip_completeness, log)
        report.results.extend(results)
        if tree is not None:
            trees.append(tree)
    manifest = workspace.ontology_manifest()
    if manifest is not None:
        report.results.extend(validate_domain_manifest(manifest, validators=v, log=log).results)
    context = CheckContext(
        workspace_root=workspace.root,
        index=Index([workspace.root]),
        trees=trees,
        workspace=workspace,
        schema_dir=v.schema_dir,
        strict=strict,
    )
    report.results.extend(run_checks(context))
    return report


def validate_repository(
    path: PathLike,
    *,
    schema_dir: Optional[PathLike] = None,
    completeness_rules: Optional[PathLike] = None,
    skip_completeness: bool = False,
    strict: bool = False,
    validators: Optional[Validators] = None,
    log: Log = _quiet,
) -> Report:
    """Validate every workspace of a Domain repository (RFC 0002 §9)."""
    v = validators or Validators(schema_dir, completeness_rules)
    repo = Path(path)
    workspaces = discover_workspaces(repo)
    report = Report(repository=repo)
    repository = ValidationResult("repository")
    domains = [w.name for w in workspaces if w.bundle_type == "domain"]
    if not domains:
        repository.add_error(
            ValidationError(
                "No Domain workspace: a Domain repository needs exactly one workspace whose "
                ".scs/config has bundle_type: domain, normally domain/",
                file_path=str(repo),
                code="DOMAIN_WORKSPACE_MISSING",
            )
        )
    elif len(domains) > 1:
        repository.add_error(
            ValidationError(
                f"{len(domains)} workspaces have bundle_type: domain ({', '.join(domains)}); "
                "a Domain repository has exactly one",
                file_path=str(repo),
                code="DOMAIN_WORKSPACE_MULTIPLE",
            )
        )
    report.results.append(repository)
    for workspace in workspaces:
        log(f"Workspace {workspace.name}")
        report.workspaces.append(_validate_workspace(workspace, v, skip_completeness, strict, log))
    return report


def find_repository(start: PathLike) -> Optional[Path]:
    """`start` if it is the root of a Domain repository, else None."""
    path = Path(start)
    return path if is_repository(path) else None
