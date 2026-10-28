# Diagnostic Codes

Every code the SCS tools emit, with its severity. Generated from
`schema/diagnostics/codes.yaml` by `skills/sync.py`; do not edit.

| Code | Severity | Meaning |
|---|---|---|
| `BUNDLE_LEGACY_CONCERN_TYPE` | error | A bundle uses the removed concern type (RFC-0001). |
| `BUNDLE_META_VERSION_INVALID` | warning | A meta bundle's version does not match the expected SCS version pattern. |
| `BUNDLE_NOT_FOUND` | error | scs bundle info names a bundle that is neither in the workspace nor a concept bundle template. |
| `BUNDLE_REQUIRED_FIELD_EMPTY` | error | A bundle's imports or scds list is empty but its type requires at least one entry. |
| `BUNDLE_SCD_UNRESOLVED` | warning | An SCD listed in a bundle could not be found. |
| `BUNDLE_STANDARDS_DEPRECATED` | warning | A bundle uses the deprecated standards type. |
| `BUNDLE_STANDARDS_SCD_DEPRECATED` | warning | A non-standards bundle lists a deprecated standards-tier SCD. |
| `BUNDLE_TOO_FEW_ITEMS` | error | A bundle's imports or scds list has fewer entries than its type requires. |
| `BUNDLE_TOO_MANY_ITEMS` | error | A bundle's imports or scds list has more entries than its type allows. |
| `BUNDLE_TYPE_MISSING` | error | A bundle has no type field. |
| `BUNDLE_TYPE_UNKNOWN` | warning | A bundle's type has no validation rules, so type-specific checks were skipped. |
| `BUNDLE_XOR_VIOLATION` | error | A bundle has both imports and scds, or neither. |
| `BUNDLE_XOR_VIOLATION_WARNING` | warning | A bundle has both imports and scds, or neither, and the rules set this check to warn. |
| `COMPILE_ERROR` | error | The bundle tree cannot be compiled (unresolved import or SCD, import cycle, DRAFT without --allow-draft, digest mismatch, or a non-compilable bundle type). |
| `COMPILE_WARNING` | warning | The compiler compiled the bundle but noted a problem with its content. |
| `COMPLETENESS_DOMAIN_MISSING` | error | A domain the completeness rules require is not imported. |
| `COMPLETENESS_DOMAIN_MISSING_WARNING` | warning | A domain the completeness rules recommend is not imported. |
| `COMPLETENESS_DOMAIN_TOO_FEW_SCDS` | error | A required domain has fewer SCDs than the completeness rules require. |
| `COMPLETENESS_DOMAIN_TOO_FEW_SCDS_WARNING` | warning | A domain has fewer SCDs than the completeness rules recommend. |
| `COMPLETENESS_RECOMMENDED_SCD_MISSING` | warning | No SCD matches a pattern the completeness rules recommend for a domain. |
| `COMPLETENESS_REQUIRED_BUNDLE_MISSING` | error | A bundle does not import the number of bundles of a type that the completeness rules require. |
| `COMPLETENESS_REQUIRED_BUNDLE_MISSING_WARNING` | warning | A bundle does not import the number of bundles of a type that the completeness rules recommend. |
| `CONCEPT_IS_A_DOMAIN` | error | The name given to scs add bundle is a domain, which is a workspace of its own (scs new domain). |
| `CONFIG_NAME_MISMATCH` | error | The name in a workspace's .scs/config differs from the workspace name, domain or its directory under projects/ (D-03). |
| `CONTENT_DIGEST_MISMATCH` | error | A versioned bundle's content no longer matches the content digest in its version manifest. |
| `CONTENT_DIGEST_UNRECORDED` | warning | A versioned bundle's manifest has no content_digest, so its content cannot be verified. |
| `DERIVED_FROM_UNRESOLVED` | warning | A derived_from entry names an intake answer or source document that is not in the workspace's intake.yaml (D-20); fails under --strict with exit code 2. |
| `DIFF_LEGACY_BASELINE` | info | The bundle has no SCS 0.7 version, so scs bundle diff compares with its pre-0.7 snapshot, which records the bundle file only; SCDs in both are listed as not compared (D-41). |
| `DIFF_VERSION_NOT_FOUND` | error | scs bundle diff was given a --from or --to version that has no tag (D-41). |
| `DOMAIN_WORKSPACE_MISSING` | error | A Domain repository has no workspace whose .scs/config bundle_type is domain, or scs new project was run outside a Domain repository. |
| `DOMAIN_WORKSPACE_MULTIPLE` | error | A Domain repository has more than one workspace whose .scs/config bundle_type is domain. |
| `DUPLICATE_ID` | error | Two documents in one workspace share an id (bundles share an id and version) (D-43). |
| `FILE_EXISTS` | error | The file the command would write already exists; pass --force to overwrite it. |
| `FILE_NOT_FOUND` | error | A file or directory named on the command line does not exist; exit code 4. |
| `FILE_UNREADABLE` | error | A file named on the command line cannot be read; exit code 4. |
| `GIT_COMMAND_FAILED` | error | A git command the engine ran failed; the message carries git's output. What the run wrote was removed. |
| `GIT_HISTORY_INCOMPLETE` | error | Repository mode in a shallow clone; version tags cannot be checked without full history and tags (D-39). |
| `GIT_REQUIRED` | error | The command needs git and git was not found. |
| `IMPORT_CYCLE` | error | Bundle imports form a cycle. |
| `IMPORT_EXISTS` | error | scs bundle add-import names a bundle that is already imported. |
| `IMPORT_EXPECTED_TYPE_MISSING` | warning | The root bundle imports no bundle of a type its own type expects. |
| `IMPORT_META_UNPINNED` | warning | A meta bundle is imported without a pinned version. |
| `IMPORT_NOT_FOUND` | error | scs bundle pin names a bundle that the bundle does not import. |
| `IMPORT_TYPE_FORBIDDEN` | error | A bundle imports a bundle type that its own type forbids. |
| `IMPORT_TYPE_LIMIT_EXCEEDED` | error | A bundle imports more bundles of one type than its own type allows. |
| `IMPORT_TYPE_NOT_ALLOWED` | error | A bundle imports a bundle type outside the types its own type allows. |
| `IMPORT_UNRESOLVED` | error | An imported bundle could not be found. |
| `IMPORT_VERSION_MISMATCH` | warning | An import pins a version different from the version of the bundle that was found. |
| `INPUT_EMPTY` | error | Content expected on stdin or in a file was empty; exit code 3. |
| `INTAKE_FIELD_RESERVED` | error | scs intake set names a field another writer owns (review_findings is written by scs intake record-finding) or that the engine sets (intake_version, scs_version). |
| `INTAKE_SCHEMA_INVALID` | error | A workspace's intake.yaml does not validate against schema/intake/intake-schema.json, or cannot be read; scs intake set and record-finding refuse a change that would make it so. |
| `INTERNAL_ERROR` | error | The tool failed unexpectedly; exit code 5. Report it with the message. |
| `MANIFEST_ALTERED` | error | The working manifest or snapshot of a version in use differs from its tagged copy, or was deleted (D-39). |
| `MANIFEST_SCHEMA_INVALID` | error | A version manifest does not validate against schema/manifest/version-manifest-schema.json (D-28, D-36). |
| `NO_INPUT` | error | The command was given nothing to act on; exit code 3. |
| `ONTOLOGY_CONCEPT_BUNDLE_MISMATCH` | error | An SCD in a concept bundle names a different concept than the one that owns the bundle. |
| `ONTOLOGY_CONCEPT_BUNDLE_MISMATCH_WARNING` | warning | An SCD in a concept bundle names a different concept than the bundle's owner, and the rules set this check to warn. |
| `ONTOLOGY_CONCEPT_ID_INVALID` | error | A concept id does not match the required pattern. |
| `ONTOLOGY_DEPENDS_ON_CYCLE` | error | depends-on relationships among concepts form a cycle. |
| `ONTOLOGY_DUPLICATE_CONCEPT_ID` | error | Two concepts in one domain share an id. |
| `ONTOLOGY_LEGACY_CONCERNS_FIELD` | error | A domain manifest has the removed concerns field (RFC-0001). |
| `ONTOLOGY_LEGACY_CONCERNS_FIELD_WARNING` | warning | A domain manifest has the removed concerns field, and the rules set this check to warn. |
| `ONTOLOGY_LEGACY_LOCATION` | info | The ontology manifest is at the 0.6 location domain/domain-manifest.yaml; 0.7 reads it from ontology/domain-manifest.yaml (D-04). |
| `ONTOLOGY_PARENT_CYCLE` | error | Concept parent links form a cycle. |
| `ONTOLOGY_PARENT_NOT_FOUND` | error | A concept's parent is not a concept in the same domain. |
| `ONTOLOGY_RELATIONSHIP_TARGET_NOT_FOUND` | error | A concept relationship targets a concept that is not in the domain. |
| `ONTOLOGY_RELATIONSHIP_TYPE_INVALID` | error | A concept relationship uses a type the ontology does not allow. |
| `ONTOLOGY_SATISFIES_TARGET_DEPRECATED` | warning | A concept's satisfies target is a deprecated standards-tier SCD instead of a std: citation. |
| `ONTOLOGY_SATISFIES_TARGET_INVALID` | error | A concept's satisfies target is not a well-formed std: citation. |
| `ONTOLOGY_SCD_CONCEPT_NOT_FOUND` | error | An SCD's concept field names a concept that is not in the domain. |
| `OUTPUT_OUTSIDE_REPO` | error | An output path is outside the repository root; SCS commands write only inside it. |
| `PARSE_FILE_NOT_FOUND` | error | The file to validate does not exist. |
| `PARSE_FILE_UNREADABLE` | error | The file to validate could not be read. |
| `PARSE_JSON_SYNTAX` | error | The file is not valid JSON. |
| `PARSE_NOT_AN_OBJECT` | error | The file parses, but its top level is not a mapping/object. |
| `PARSE_YAML_SYNTAX` | error | The file is not valid YAML. |
| `PROVENANCE_PLACEHOLDER` | warning | A working SCD or bundle has a placeholder created_by (developer, an empty name, or an example or invalid domain) (D-71). |
| `RELATIONSHIP_CITATION_INVALID` | error | A std: citation target is not in the std:<standard>[:<edition>][#<clause>] form. |
| `RELATIONSHIP_CITATION_WRONG_TYPE` | error | A std: citation is the target of a relationship other than satisfies. |
| `RELATIONSHIP_CYCLE` | warning | SCD relationships form a circular dependency. |
| `RELATIONSHIP_SELF_REFERENCE` | error | An SCD has a relationship to itself. |
| `RELATIONSHIP_STANDARDS_TARGET_DEPRECATED` | warning | A relationship targets a deprecated standards-tier SCD instead of a std: citation. |
| `RELATIONSHIP_TARGET_MISSING` | error | An SCD relationship has no target field. |
| `RELATIONSHIP_TARGET_NOT_FOUND` | error | A relationship target SCD does not exist in a complete project. |
| `RELATIONSHIP_TARGET_NOT_IN_BUNDLE` | warning | A relationship target SCD is not in this standalone bundle and may live in another bundle. |
| `RELATIONSHIP_TIER_CONSTRAINT` | error | A relationship links SCD tiers that its type does not allow. |
| `RELATIONSHIP_TYPE_INVALID` | error | An SCD relationship uses a type that is not defined in the relationship rules. |
| `RELATIONSHIP_TYPE_MISSING` | error | An SCD relationship has no type field. |
| `RESERVED_BUNDLE_NAME` | error | A bundle is named plan, test-plan, or qa, which are reserved for a later release (D-33). |
| `RULES_DIR_NOT_FOUND` | error | The validation rules directory does not exist. |
| `RULES_FILE_NOT_FOUND` | error | A validation rules file is missing from the rules directory. |
| `RULES_LOAD_FAILED` | error | A validation rules file (built-in, project, or custom completeness rules) could not be read or parsed. |
| `SCD_ALREADY_LISTED` | error | scs bundle add-scd names an SCD the bundle already lists. |
| `SCD_DUPLICATE_ENTRY_ID` | error | Two directives, prohibitions, or facts in one SCD share an id. |
| `SCD_EMPTY` | info | An SCD has no prohibitions, directives, or facts, so it contributes nothing to a compiled artifact (D-70). |
| `SCD_FIELD_EMPTY` | error | A required string field (title or description) of an SCD is blank. |
| `SCD_ID_INVALID` | error | An SCD id does not match the scd:<tier>:<name> format. |
| `SCD_ID_MISSING` | error | An SCD has no id field. |
| `SCD_NOT_FOUND` | error | scs bundle add-scd names an SCD that is not in the workspace. |
| `SCD_NOT_LISTED` | error | scs bundle remove-scd names an SCD that the bundle (or any bundle) does not list. |
| `SCD_PROHIBITION_NOT_BINARY` | error | A prohibition's subject contains a condition or qualifier instead of stating exactly what is prohibited. |
| `SCD_PROVENANCE_CREATED_BY_MISSING` | error | An SCD's provenance has no created_by value. |
| `SCD_PROVENANCE_EMPTY` | warning | An SCD's provenance section is present but empty. |
| `SCD_PROVENANCE_RATIONALE_MISSING` | warning | An SCD's provenance has no rationale, which is recommended. |
| `SCD_PROVENANCE_TIMESTAMP_INVALID` | error | A provenance timestamp is not valid ISO 8601. |
| `SCD_STANDARDS_TIER_DEPRECATED` | warning | An SCD uses the standards tier, deprecated since 0.6.0 in favour of std: citations. |
| `SCD_TYPE_MISSING` | error | An SCD has no type field. |
| `SCD_TYPE_TIER_MISMATCH` | error | An SCD's type does not match the tier in its id. |
| `SCD_VERSION_INVALID` | error | An SCD version is neither DRAFT nor a valid semantic version. |
| `SCHEMA_BUNDLE_INVALID` | error | A bundle does not validate against the bundle JSON Schema. |
| `SCHEMA_CHECKPOINT_RECORD_INVALID` | error | A checkpoint record does not validate against the checkpoint record JSON Schema. |
| `SCHEMA_DIR_NOT_FOUND` | error | No SCS JSON Schema directory was found (--schema-dir, SCS_SCHEMA_DIR, discovery, or the packaged copy); exit code 4. |
| `SCHEMA_DOMAIN_MANIFEST_INVALID` | error | A domain manifest does not validate against the domain manifest JSON Schema. |
| `SCHEMA_LOAD_FAILED` | error | A JSON Schema file the validator needs could not be read or is not valid JSON. |
| `SCHEMA_NOT_FOUND` | error | A JSON Schema file the validator needs could not be found. |
| `SCHEMA_SCD_INVALID` | error | An SCD does not validate against the JSON Schema for its tier. |
| `SCHEMA_VALIDATION_FAILED` | error | Schema validation itself failed with an unexpected exception, so the document was not checked. |
| `STACK_ARTIFACT_INVALID` | error | An input to scs stack is not a runtime artifact (not YAML or JSON, or not valid against schema/runtime/runtime-artifact-schema.json). |
| `STACK_BUNDLE_REPEATED` | error | The same bundle id appears in two layers of a stack, for example two versions of one bundle. |
| `STACK_LAYER_DRAFT` | info | A layer of a stack is a DRAFT artifact (version DRAFT+<digest>). |
| `STACK_PROHIBITION_DIRECTED` | warning | A directive in one layer of a stack contains, ignoring case, the subject of a prohibition in another layer; a textual match that the advisory review judges (layer-conflict). |
| `STACK_RULE_DUPLICATE` | info | Two layers of a stack carry a rule or fact with identical text, for example the meta bundle's rules in two Domain artifacts. |
| `TEMPLATE_NOT_FOUND` | error | No SCD or concept bundle template has the given name in the workspace's ontology model. |
| `USAGE_ERROR` | error | The command line is wrong (unknown option, missing argument, conflicting options); exit code 3. |
| `VERSION_APPROVER_INVALID` | error | The approver is not a person identifier, Name <email> (D-28). |
| `VERSION_APPROVER_REQUIRED` | error | scs bundle version was run without an approver; name one with --approved-by (D-13). |
| `VERSION_EXISTS` | error | The version already exists (its tag, snapshot, or manifest); versions are never overwritten (D-15). |
| `VERSION_IMPORT_NOT_PINNED` | error | The bundle being versioned imports a bundle without a version, at DRAFT, or that does not resolve (D-14). |
| `VERSION_INPUT_UNTRACKED` | error | A file the content digest or the compiler reads is ignored by git, so the version commit would not hold it (D-40). |
| `VERSION_INVALID` | error | The version is not MAJOR.MINOR.PATCH; exit code 3. |
| `VERSION_MANIFEST_INCOMPLETE` | error | A manifest with a workspace-qualified tag lacks content_digest or tools_version, which every 0.7 manifest carries (D-49). |
| `VERSION_MANIFEST_MISSING` | error | A workspace-qualified version tag points at a commit without that version's manifest (D-39). |
| `VERSION_NOT_FOUND` | error | No version tag exists for the requested version. |
| `VERSION_PROVENANCE_PLACEHOLDER` | error | The bundle or one of its SCDs has a placeholder created_by; correct it before versioning (D-71). |
| `VERSION_TAG_MISSING` | error | A manifest records a content digest but its version tag does not exist, or a pinned import has no 0.7 tag (D-39). |
| `WORKSPACE_CONFIG_INVALID` | error | A workspace's .scs/config cannot be read as key-value pairs. |
| `WORKSPACE_EXISTS` | error | The Domain repository or Project workspace scs new would create already exists. |
| `WORKSPACE_FILE_UNREADABLE` | warning | A YAML file in the workspace could not be read or parsed and was skipped, so any SCD or bundle in it is not seen; fix it or delete it. |
| `WORKSPACE_NAME_INVALID` | error | A Domain or Project name cannot be a directory, bundle id, and tag prefix (bad characters), names a concept bundle, or is a Project named domain; exit code 3. |
| `WORKSPACE_NOT_FOUND` | error | No workspace was found (no .scs/config above the current directory, or no workspace by the --workspace name). |
| `WORKSPACE_REQUIRED` | error | At the root of a Domain repository a workspace-scoped command needs --workspace (D-42); exit code 3. |
