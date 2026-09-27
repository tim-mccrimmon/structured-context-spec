"""Domain Ontology validation module (RFC-0001)."""

import re
from typing import Any, Dict, List, Optional, Set

from .rules_loader import RulesLoader
from .utils import ValidationError, ValidationResult, ValidationWarning


class OntologyValidator:
    """Validator for the Domain Ontology (RFC-0001 Validation rules 1-8)."""

    def __init__(self, rules_loader: RulesLoader):
        """Initialize ontology validator.

        Args:
            rules_loader: Rules loader instance
        """
        self.rules_loader = rules_loader
        self.rules = rules_loader.load_domain_ontology_rules()

    def validate_domain_manifest(
        self,
        manifest: Dict[str, Any],
        file_path: str | None = None,
        scds: Optional[List[Dict[str, Any]]] = None,
        bundles: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """Validate a domain manifest's ontology.

        Args:
            manifest: Parsed domain manifest (top-level dict with a "domain" key)
            file_path: Optional file path for error messages
            scds: Optional list of loaded SCDs, to check rule 6 (SCD concept
                resolution) and (with bundles) rule 7 (concept-bundle agreement)
            bundles: Optional list of loaded bundles, to check rule 7

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult("ontology")

        domain = manifest.get("domain", {})
        domain_id = domain.get("id", "unknown")

        # Rule 8: concern residue - checked regardless of whether ontology is present
        self._check_concern_residue(domain, result, file_path)

        ontology = domain.get("ontology")
        if not ontology:
            # No ontology block - schema_validator already flags this as a
            # missing required field; nothing further to check here.
            return result

        concepts = ontology.get("concepts", [])
        relationship_types = ontology.get(
            "relationship_types", self.rules.get("relationship_types", {}).get("default", [])
        )

        # Rule 1
        concept_ids = self._validate_ids_and_uniqueness(concepts, domain_id, result, file_path)

        # Rule 2
        self._validate_parent_taxonomy(concepts, concept_ids, domain_id, result, file_path)

        # Rules 3 + 4
        self._validate_relationships(
            concepts, concept_ids, relationship_types, domain_id, result, file_path
        )

        # Rule 5
        self._validate_depends_on_acyclic(concepts, result, file_path)

        # Rule 6 (best-effort: only when SCDs are supplied)
        if scds is not None:
            self._validate_scd_concept_resolution(scds, concept_ids, domain_id, result, file_path)

        # Rule 7 (best-effort: only when both SCDs and bundles are supplied)
        if scds is not None and bundles is not None:
            self._validate_concept_bundle_agreement(concepts, scds, bundles, result, file_path)

        return result

    def _check_concern_residue(
        self, domain: Dict[str, Any], result: ValidationResult, file_path: str | None
    ) -> None:
        """Rule 8: legacy 'concerns' field in a domain manifest is an error."""
        rule = self.rules.get("concern_residue", {})
        if not rule.get("enabled", True):
            return

        if "concerns" in domain:
            msg = self.rules_loader.get_error_message(self.rules, "legacy_concerns_field")
            severity = rule.get("severity", "error")
            if severity == "error":
                result.add_error(ValidationError(msg, file_path=file_path))
            else:
                result.add_warning(ValidationWarning(msg, level="ontology", file_path=file_path))

    def _validate_ids_and_uniqueness(
        self,
        concepts: List[Dict[str, Any]],
        domain_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> Set[str]:
        """Rule 1: concept id format + uniqueness within the domain."""
        pattern = self.rules.get("id_pattern", {}).get("pattern", r"^concept:[a-z][a-z0-9-]*$")
        seen: Set[str] = set()
        valid_ids: Set[str] = set()

        for concept in concepts:
            concept_id = concept.get("id")
            if not concept_id:
                continue  # caught by schema validation (required field)

            if not re.match(pattern, concept_id):
                msg = self.rules_loader.get_error_message(
                    self.rules, "invalid_concept_id", concept_id=concept_id, pattern=pattern
                )
                result.add_error(ValidationError(msg, file_path=file_path))
                continue  # malformed ids don't join the valid set

            if concept_id in seen:
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "duplicate_concept_id",
                    concept_id=concept_id,
                    domain_id=domain_id,
                )
                result.add_error(ValidationError(msg, file_path=file_path))

            seen.add(concept_id)
            valid_ids.add(concept_id)

        return valid_ids

    def _validate_parent_taxonomy(
        self,
        concepts: List[Dict[str, Any]],
        concept_ids: Set[str],
        domain_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Rule 2: parent resolves to a concept in the same domain; acyclic."""
        rule = self.rules.get("parent_taxonomy", {})
        resolution_rule = rule.get("resolution", {})
        acyclic_rule = rule.get("acyclic", {})

        parent_graph: Dict[str, List[str]] = {}

        for concept in concepts:
            concept_id = concept.get("id")
            parent_id = concept.get("parent")
            if not concept_id or not parent_id:
                continue

            if resolution_rule.get("enabled", True) and parent_id not in concept_ids:
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "parent_not_found",
                    concept_id=concept_id,
                    parent_id=parent_id,
                    domain_id=domain_id,
                )
                result.add_error(ValidationError(msg, file_path=file_path))
                continue  # don't walk an unresolved edge for cycle detection

            parent_graph[concept_id] = [parent_id]

        if acyclic_rule.get("enabled", True):
            cycle = self._find_cycle(parent_graph)
            if cycle:
                msg = self.rules_loader.get_error_message(
                    self.rules, "parent_cycle", cycle=" -> ".join(cycle)
                )
                result.add_error(ValidationError(msg, file_path=file_path))

    def _validate_relationships(
        self,
        concepts: List[Dict[str, Any]],
        concept_ids: Set[str],
        relationship_types: List[str],
        domain_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Rules 3 + 4: relationship type is allowed; target resolves.

        The `satisfies[]` shorthand is sugar for a `relationships` entry of
        type `satisfies` (RFC-0001, kept per the Phase 0 decision) - each
        entry gets the same validation as an equivalent relationships entry.
        """
        for concept in concepts:
            concept_id = concept.get("id")
            if not concept_id:
                continue

            for rel in concept.get("relationships", []):
                rel_type = rel.get("type")
                target = rel.get("target")
                if not rel_type or not target:
                    continue  # caught by schema validation
                self._validate_single_relationship(
                    concept_id,
                    rel_type,
                    target,
                    concept_ids,
                    relationship_types,
                    domain_id,
                    result,
                    file_path,
                )

            for target in concept.get("satisfies", []):
                if not target:
                    continue
                self._validate_single_relationship(
                    concept_id,
                    "satisfies",
                    target,
                    concept_ids,
                    relationship_types,
                    domain_id,
                    result,
                    file_path,
                )

    def _validate_single_relationship(
        self,
        concept_id: str,
        rel_type: str,
        target: str,
        concept_ids: Set[str],
        relationship_types: List[str],
        domain_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate one (type, target) edge, whether from `relationships[]`
        or expanded from the `satisfies[]` shorthand."""
        rel_rules = self.rules.get("relationship_targets", {})

        if rel_type not in relationship_types:
            msg = self.rules_loader.get_error_message(
                self.rules,
                "invalid_relationship_type",
                concept_id=concept_id,
                type=rel_type,
                allowed_types=", ".join(relationship_types),
            )
            result.add_error(ValidationError(msg, file_path=file_path))
            return

        type_rule = rel_rules.get(rel_type, {})
        target_kind = type_rule.get("target_kind")

        if target_kind == "concept":
            if target not in concept_ids:
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "relationship_target_not_found",
                    concept_id=concept_id,
                    type=rel_type,
                    target=target,
                    domain_id=domain_id,
                )
                result.add_error(ValidationError(msg, file_path=file_path))

        elif target_kind == "scd:standards":
            if not target.startswith("scd:standards:"):
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "relationship_target_not_found",
                    concept_id=concept_id,
                    type=rel_type,
                    target=target,
                    domain_id=domain_id,
                )
                result.add_error(ValidationError(msg, file_path=file_path))
            else:
                # Well-formed scd:standards: id. Resolving it against real
                # SCDs needs project-level context this validator doesn't
                # have when called with only a domain manifest - flag as a
                # soft warning, not an error, consistent with how
                # relationship_validator treats unresolved cross-bundle
                # targets.
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "satisfies_target_unresolved",
                    concept_id=concept_id,
                    target=target,
                )
                result.add_warning(ValidationWarning(msg, level="ontology", file_path=file_path))

    def _validate_depends_on_acyclic(
        self,
        concepts: List[Dict[str, Any]],
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Rule 5: depends-on relationships among concepts must be acyclic."""
        rule = self.rules.get("depends_on_cycle_detection", {})
        if not rule.get("enabled", True):
            return

        graph: Dict[str, List[str]] = {}
        for concept in concepts:
            concept_id = concept.get("id")
            if not concept_id:
                continue

            targets = [
                rel.get("target")
                for rel in concept.get("relationships", [])
                if rel.get("type") == "depends-on" and rel.get("target")
            ]
            if targets:
                graph[concept_id] = targets

        cycle = self._find_cycle(graph)
        if cycle:
            msg = self.rules_loader.get_error_message(
                self.rules, "depends_on_cycle", cycle=" -> ".join(cycle)
            )
            result.add_error(ValidationError(msg, file_path=file_path))

    def _validate_scd_concept_resolution(
        self,
        scds: List[Dict[str, Any]],
        concept_ids: Set[str],
        domain_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Rule 6: an SCD's concept field, if present, resolves in the domain."""
        rule = self.rules.get("scd_concept_resolution", {})
        if not rule.get("enabled", True):
            return

        for scd in scds:
            concept_id = scd.get("concept")
            if not concept_id:
                continue

            if concept_id not in concept_ids:
                scd_id = scd.get("id", "unknown")
                msg = self.rules_loader.get_error_message(
                    self.rules,
                    "scd_concept_not_found",
                    scd_id=scd_id,
                    concept_id=concept_id,
                    domain_id=domain_id,
                )
                result.add_error(ValidationError(msg, scd_id=scd_id, file_path=file_path))

    def _validate_concept_bundle_agreement(
        self,
        concepts: List[Dict[str, Any]],
        scds: List[Dict[str, Any]],
        bundles: List[Dict[str, Any]],
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Rule 7 (SHOULD, warning): a concept bundle's SCDs should all
        declare the same concept as the bundle they're in.

        The bundle -> concept mapping comes from the ontology's
        concepts[].bundle field (bundles don't carry a concept field of
        their own), matched by stripping the version suffix.
        """
        rule = self.rules.get("concept_bundle_agreement", {})
        if not rule.get("enabled", True):
            return

        severity = rule.get("severity", "warning")

        def unversioned(bundle_ref: str) -> str:
            parts = bundle_ref.split(":")
            return ":".join(parts[:2]) if len(parts) >= 2 else bundle_ref

        bundle_to_concept = {
            unversioned(concept["bundle"]): concept["id"]
            for concept in concepts
            if concept.get("bundle") and concept.get("id")
        }

        scd_lookup = {scd.get("id"): scd for scd in scds if scd.get("id")}

        for bundle in bundles:
            if bundle.get("type") != "concept":
                continue

            bundle_id = bundle.get("id", "unknown")
            owning_concept = bundle_to_concept.get(unversioned(bundle_id))
            if not owning_concept:
                continue  # this bundle isn't referenced by any concept in this domain

            for scd_ref in bundle.get("scds", []):
                scd = scd_lookup.get(scd_ref)
                if not scd:
                    continue

                scd_concept = scd.get("concept")
                if scd_concept and scd_concept != owning_concept:
                    msg = self.rules_loader.get_error_message(
                        self.rules,
                        "concept_bundle_mismatch",
                        scd_id=scd.get("id", "unknown"),
                        bundle_id=bundle_id,
                        scd_concept=scd_concept,
                        bundle_concept=owning_concept,
                    )
                    if severity == "error":
                        result.add_error(ValidationError(msg, file_path=file_path))
                    else:
                        result.add_warning(
                            ValidationWarning(msg, level="ontology", file_path=file_path)
                        )

    @staticmethod
    def _find_cycle(graph: Dict[str, List[str]]) -> Optional[List[str]]:
        """Find a cycle in a directed graph via DFS, if one exists.

        Args:
            graph: Adjacency list, node id -> list of target node ids

        Returns:
            The cycle as a list of node ids (closing back on itself), or None
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    found = dfs(neighbor, path[:])
                    if found:
                        return found
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            rec_stack.discard(node)
            return None

        for node in graph:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    return cycle

        return None
