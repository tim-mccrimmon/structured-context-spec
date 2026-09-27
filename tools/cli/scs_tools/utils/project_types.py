"""Project type configurations for SCS 0.5.0"""

from typing import Dict, List

PROJECT_TYPES = {
    "healthcare": {
        "description": "Healthcare application (HIPAA, CHAI, TEFCA)",
        "domains": ["software-development"],  # Can add clinical domain later
        "compliance_bundles": [
            "hipaa-compliance",
            "chai-adherence",
            "soc2-controls",
            "tefca-participation",
        ],
        "exclude_scds": [],
    },
    "fintech": {
        "description": "Financial services application (PCI-DSS, SOX)",
        "domains": ["software-development"],  # Can add financial domain later
        "compliance_bundles": ["pci-dss-compliance", "sox-controls", "soc2-controls"],
        "exclude_scds": ["chai-adherence", "tefca-participation"],
    },
    "saas": {
        "description": "SaaS product (GDPR, SOC2, multi-tenancy)",
        "domains": ["software-development"],
        "compliance_bundles": ["gdpr-compliance", "soc2-controls"],
        "exclude_scds": ["hipaa-compliance", "chai-adherence", "tefca-participation"],
    },
    "government": {
        "description": "Government application (NIST, FedRAMP)",
        "domains": ["software-development"],
        "compliance_bundles": ["nist-800-53", "fedramp-controls"],
        "exclude_scds": ["hipaa-compliance", "chai-adherence", "tefca-participation"],
    },
    "minimal": {
        "description": "Minimal project (essential concepts only)",
        "domains": ["software-development"],  # Still uses domain, but with fewer concepts
        "minimal_concepts": ["architecture", "security", "deployment-operations"],
        "compliance_bundles": [],
        "exclude_scds": [],
        "minimal": True,
    },
    "standard": {
        "description": "Standard software development project (all 11 concepts)",
        "domains": ["software-development"],
        "compliance_bundles": ["soc2-controls"],
        "exclude_scds": ["hipaa-compliance", "chai-adherence", "tefca-participation"],
    },
}


# The 11 concepts within the Software Development domain (RFC-0001 Domain Ontology)
SOFTWARE_DEVELOPMENT_CONCEPTS = [
    "business-context",
    "architecture",
    "security",
    "performance-reliability",
    "usability-accessibility",
    "compliance-governance",
    "data-provenance",
    "testing-validation",
    "deployment-operations",
    "safety-risk",
    "ethics-ai-accountability",
]


# Names and descriptions of the 11 concepts, as in the reference ontology
# (schema/domain/examples/software-development-domain.yaml; a test keeps them in step)
SOFTWARE_DEVELOPMENT_CONCEPT_INFO = {
    "business-context": ("Business Context", "Problem, stakeholders, objectives, and opportunity."),
    "architecture": (
        "Architecture",
        "System structure, components, boundaries, and technical design.",
    ),
    "security": ("Security", "Authentication, authorization, encryption, and data protection."),
    "performance-reliability": (
        "Performance & Reliability",
        "Performance requirements, reliability targets, and scalability.",
    ),
    "usability-accessibility": (
        "Usability & Accessibility",
        "User experience, interface design, and accessibility requirements.",
    ),
    "compliance-governance": (
        "Compliance & Governance",
        "Regulatory compliance, audit requirements, and governance policies.",
    ),
    "data-provenance": (
        "Data & Provenance",
        "Data models, data flow, data governance, and provenance tracking.",
    ),
    "testing-validation": (
        "Testing & Validation",
        "Testing strategy, validation approach, and quality assurance.",
    ),
    "deployment-operations": (
        "Deployment & Operations",
        "Deployment strategy, operational procedures, and monitoring.",
    ),
    "safety-risk": ("Safety & Risk", "Safety requirements, risk assessment, and hazard analysis."),
    "ethics-ai-accountability": (
        "Ethics & AI Accountability",
        "Ethical considerations, AI/ML governance, and bias mitigation.",
    ),
}


# The 16 concepts within the Merchant Cash Advance domain (RFC-0001 Domain Ontology).
# Auto-generated from schema/domain/examples/merchant-cash-advance-domain.yaml;
# a test keeps this in step with that file.
MCA_CONCEPTS = [
    "origination",
    "underwriting-decisioning",
    "contract-characterization",
    "disclosure-compliance",
    "security-interest-management",
    "servicing-collections",
    "capital-funding",
    "portfolio-risk-management",
    "broker-partner-management",
    "data-provenance",
    "data-security",
    "systems-integration",
    "governance",
    "ai-accountability",
    "training-competency",
    "adoption-rollout",
]

MCA_CONCEPT_INFO = {
    "origination": (
        "Origination",
        "ISO/broker intake, lead qualification, and application intake.",
    ),
    "underwriting-decisioning": (
        "Underwriting & Decisioning",
        "Cash-flow analysis, risk scoring, approve/decline/counter, and pricing and terms.",
    ),
    "contract-characterization": (
        "Contract Characterization",
        "The true-sale and reconciliation-provision discipline that keeps a deal a purchase of "
        "receivables, not a loan.",
    ),
    "disclosure-compliance": (
        "Disclosure Compliance",
        "State commercial-financing disclosure requirements.",
    ),
    "security-interest-management": (
        "Security Interest Management",
        "UCC-1 filings and liens on receivables: perfection, and releases on payoff.",
    ),
    "servicing-collections": (
        "Servicing & Collections",
        "Daily or twice-monthly ACH debiting, NSF and returns, delinquency, restructuring, and "
        "confession-of-judgment posture.",
    ),
    "capital-funding": (
        "Capital & Funding",
        "Where the funder's own money comes from to fund merchants: credit facilities, warehouse "
        "lines, and Treasury.",
    ),
    "portfolio-risk-management": (
        "Portfolio Risk Management",
        "Aggregate credit and default risk across the book (distinct from AI operational risk, "
        "which lives under ai-accountability).",
    ),
    "broker-partner-management": (
        "Broker & Partner Management",
        "ISO and broker relationships, and oversight of what brokers represent to merchants.",
    ),
    "data-provenance": (
        "Data & Provenance",
        "Bank-statement data, credit-bureau pulls, and ISO/broker-submitted application data: "
        "where it comes from and what AI may do with it.",
    ),
    "data-security": (
        "Data Security",
        "Merchant PII, guarantor PII, and bank data: access boundaries at the AI layer.",
    ),
    "systems-integration": (
        "Systems Integration",
        "How AI plugs into the loan-origination, CRM, and ACH/servicing platforms, including how "
        "state data is looked up at the moment a prompt is assembled.",
    ),
    "governance": (
        "Governance",
        'Which AI tools are sanctioned, the autonomy default for AI use, and the hard "never" '
        "prohibitions company-wide.",
    ),
    "ai-accountability": (
        "AI Accountability",
        "The company AI use policy. The human is the author of record, AI augments judgment and "
        "does not replace sign-off authority, chain of custody, and the human-review thresholds "
        "before an AI-assisted recommendation becomes an approve/decline/fund action.",
    ),
    "training-competency": (
        "Training & Competency",
        "Role-based training, meaning what leadership and staff need to know before using AI.",
    ),
    "adoption-rollout": (
        "Adoption & Rollout",
        "Phased AI rollout per department, with rollback triggers if a workflow is not working.",
    ),
}

# Concept id -> its outgoing relationships (depends-on / relates-to), matching the domain
# manifest exactly. No satisfies (best-practice AI governance, not a compliance mapping -
# see the source ontology).
MCA_CONCEPT_RELATIONSHIPS: Dict[str, List[Dict[str, str]]] = {
    "origination": [
        {"type": "depends-on", "target": "concept:data-provenance"},
        {"type": "relates-to", "target": "concept:underwriting-decisioning"},
    ],
    "underwriting-decisioning": [
        {"type": "depends-on", "target": "concept:data-provenance"},
        {"type": "relates-to", "target": "concept:contract-characterization"},
        {"type": "relates-to", "target": "concept:portfolio-risk-management"},
    ],
    "contract-characterization": [
        {"type": "relates-to", "target": "concept:disclosure-compliance"},
    ],
    "security-interest-management": [
        {"type": "relates-to", "target": "concept:portfolio-risk-management"},
    ],
    "servicing-collections": [
        {"type": "depends-on", "target": "concept:security-interest-management"},
        {"type": "relates-to", "target": "concept:contract-characterization"},
    ],
    "capital-funding": [
        {"type": "relates-to", "target": "concept:portfolio-risk-management"},
    ],
    "broker-partner-management": [
        {"type": "relates-to", "target": "concept:origination"},
        {"type": "relates-to", "target": "concept:disclosure-compliance"},
    ],
    "data-provenance": [
        {"type": "depends-on", "target": "concept:systems-integration"},
    ],
    "data-security": [
        {"type": "depends-on", "target": "concept:systems-integration"},
    ],
    "adoption-rollout": [
        {"type": "relates-to", "target": "concept:governance"},
    ],
}


# Ontology models a project can be scaffolded against. "sdlc" is the default and the only
# one PROJECT_TYPES variants (healthcare/fintech/saas/government/minimal) apply to - they're
# all software-development-flavored. "mca" has one shape: all 16 concepts, no variants yet.
ONTOLOGY_MODELS = {
    "sdlc": {
        "description": "Software Development (default) - supports --type variants",
        "domain": "software-development",
        "domain_name": "Software Development",
        "concepts": SOFTWARE_DEVELOPMENT_CONCEPTS,
        "concept_info": SOFTWARE_DEVELOPMENT_CONCEPT_INFO,
        "relationships": {},
    },
    "mca": {
        "description": "Merchant Cash Advance / business funding - all 16 concepts, no --type"
        " variants",
        "domain": "merchant-cash-advance",
        "domain_name": "Merchant Cash Advance",
        "concepts": MCA_CONCEPTS,
        "concept_info": MCA_CONCEPT_INFO,
        "relationships": MCA_CONCEPT_RELATIONSHIPS,
    },
}


def get_ontology_model_config(model: str) -> Dict:
    """Get the configuration for an ontology model ('sdlc', 'mca', ...)."""
    return ONTOLOGY_MODELS.get(model, ONTOLOGY_MODELS["sdlc"])


def get_concept_info(concepts, concept_info_map=None, relationships_map=None):
    """Ontology entries (id, name, description, and optional relationships) for the given
    concept ids, in the order given. Defaults to the Software Development concept info for
    backwards compatibility; pass concept_info_map/relationships_map for another model."""
    info_map = (
        concept_info_map if concept_info_map is not None else SOFTWARE_DEVELOPMENT_CONCEPT_INFO
    )
    rel_map = relationships_map or {}
    return [
        {
            "id": c,
            "name": info_map[c][0],
            "description": info_map[c][1],
            "relationships": rel_map.get(c, []),
        }
        for c in concepts
    ]


# Minimal set of concepts for early-stage projects
MINIMAL_CONCEPTS = [
    "architecture",
    "security",
    "deployment-operations",
]


# Available domains (SCS 0.5.0 - multi-domain architecture, RFC-0001 Domain Ontology)
AVAILABLE_DOMAINS = {
    "software-development": {
        "name": "Software Development",
        "description": "Software engineering practices, architecture, testing, deployment",
        "concepts": SOFTWARE_DEVELOPMENT_CONCEPTS,
    },
    # Future domains to be added by domain experts:
    # "legal": {...},
    # "clinical": {...},
    # "financial": {...},
}


def get_domains_for_project_type(project_type: str) -> List[str]:
    """Get the list of domain bundles for a project type.

    In SCS 0.5.0, projects import domain bundles (e.g., software-development),
    which in turn import concept bundles (e.g., architecture, security).
    """
    config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])
    return config.get("domains", ["software-development"])


def get_concepts_for_project_type(project_type: str) -> List[str]:
    """Get the list of concept bundles for a project type.

    This is used when generating concept bundles for a project.
    For minimal projects, returns only essential concepts.
    For full projects, returns all concepts in the software-development domain.
    """
    config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])

    if config.get("minimal"):
        return config.get("minimal_concepts", MINIMAL_CONCEPTS)

    # Default: all concepts in software-development domain
    return SOFTWARE_DEVELOPMENT_CONCEPTS


def get_bundles_for_project_type(project_type: str) -> List[str]:
    """Get the list of bundles to import in the project bundle.

    DEPRECATED in 0.3: Use get_domains_for_project_type() instead.
    This function is maintained for backward compatibility and returns
    domain bundles, not concept bundles.
    """
    return get_domains_for_project_type(project_type)


def get_project_type_config(project_type: str) -> Dict:
    """Get the configuration for a project type"""
    return PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])


def get_domain_config(domain_name: str) -> Dict:
    """Get configuration for a specific domain"""
    return AVAILABLE_DOMAINS.get(domain_name, AVAILABLE_DOMAINS["software-development"])
