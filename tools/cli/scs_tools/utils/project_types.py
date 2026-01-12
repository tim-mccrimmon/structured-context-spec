"""Project type configurations for SCS 0.3"""

from typing import Dict, List


PROJECT_TYPES = {
    "healthcare": {
        "description": "Healthcare application (HIPAA, CHAI, TEFCA)",
        "domains": ["software-development"],  # Can add clinical domain later
        "compliance_bundles": ["hipaa-compliance", "chai-adherence", "soc2-controls", "tefca-participation"],
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
        "description": "Minimal project (essential concerns only)",
        "domains": ["software-development"],  # Still uses domain, but with fewer concerns
        "minimal_concerns": ["architecture", "security", "deployment-operations"],
        "compliance_bundles": [],
        "exclude_scds": [],
        "minimal": True,
    },
    "standard": {
        "description": "Standard software development project (all 11 concerns)",
        "domains": ["software-development"],
        "compliance_bundles": ["soc2-controls"],
        "exclude_scds": ["hipaa-compliance", "chai-adherence", "tefca-participation"],
    },
}


# The 11 concerns within the Software Development domain
SOFTWARE_DEVELOPMENT_CONCERNS = [
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


# Minimal set of concerns for early-stage projects
MINIMAL_CONCERNS = [
    "architecture",
    "security",
    "deployment-operations",
]


# Available domains (SCS 0.3 - multi-domain architecture)
AVAILABLE_DOMAINS = {
    "software-development": {
        "name": "Software Development",
        "description": "Software engineering practices, architecture, testing, deployment",
        "concerns": SOFTWARE_DEVELOPMENT_CONCERNS,
    },
    # Future domains to be added by domain experts:
    # "legal": {...},
    # "clinical": {...},
    # "financial": {...},
}


def get_domains_for_project_type(project_type: str) -> List[str]:
    """Get the list of domain bundles for a project type.

    In SCS 0.3, projects import domain bundles (e.g., software-development),
    which in turn import concern bundles (e.g., architecture, security).
    """
    config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])
    return config.get("domains", ["software-development"])


def get_concerns_for_project_type(project_type: str) -> List[str]:
    """Get the list of concern bundles for a project type.

    This is used when generating concern bundles for a project.
    For minimal projects, returns only essential concerns.
    For full projects, returns all concerns in the software-development domain.
    """
    config = PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])

    if config.get("minimal"):
        return config.get("minimal_concerns", MINIMAL_CONCERNS)

    # Default: all concerns in software-development domain
    return SOFTWARE_DEVELOPMENT_CONCERNS


def get_bundles_for_project_type(project_type: str) -> List[str]:
    """Get the list of bundles to import in the project bundle.

    DEPRECATED in 0.3: Use get_domains_for_project_type() instead.
    This function is maintained for backward compatibility and returns
    domain bundles, not concern bundles.
    """
    return get_domains_for_project_type(project_type)


def get_project_type_config(project_type: str) -> Dict:
    """Get the configuration for a project type"""
    return PROJECT_TYPES.get(project_type, PROJECT_TYPES["standard"])


def get_domain_config(domain_name: str) -> Dict:
    """Get configuration for a specific domain"""
    return AVAILABLE_DOMAINS.get(domain_name, AVAILABLE_DOMAINS["software-development"])
