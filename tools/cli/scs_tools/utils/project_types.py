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


def get_concept_info(concepts):
    """Ontology entries (id, name, description) for the given concept ids, in the order given"""
    return [
        {
            "id": c,
            "name": SOFTWARE_DEVELOPMENT_CONCEPT_INFO[c][0],
            "description": SOFTWARE_DEVELOPMENT_CONCEPT_INFO[c][1],
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
