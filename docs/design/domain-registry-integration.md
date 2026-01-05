# Domain Registry Integration Design

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Overview

This document defines how SCS integrates with the domain registry for discovering, installing, and managing domains.

**Key Requirements:**
- Discover available domains (both free and commercial)
- Install/uninstall domains
- Verify domain licenses (for commercial domains)
- Update domains to newer versions
- Support both online (registry) and offline (local) domains

---

## 2. Registry Architecture

### 2.1 Registry Components

```
┌─────────────────────────────────────────────────┐
│           Domain Registry Service                │
│  (https://registry.scs-commercial.com)          │
│                                                  │
│  - Domain catalog API                           │
│  - License verification API                     │
│  - Domain download/distribution                 │
│  - Version management                           │
└─────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────┐
│              SCS CLI Client                      │
│                                                  │
│  - Registry client library                      │
│  - Local domain cache                           │
│  - License management                           │
│  - Domain loader                                │
└─────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────┐
│          Local Domain Storage                    │
│  ~/.scs/domains/                                │
│    ├── software-development/                    │
│    ├── healthcare/                              │
│    └── sales/                                   │
└─────────────────────────────────────────────────┘
```

### 2.2 Domain Storage Structure

```
~/.scs/
├── config.yaml                    # Global SCS configuration
├── licenses/                      # License keys for commercial domains
│   ├── healthcare.license
│   └── sales.license
├── domains/                       # Installed domains
│   ├── software-development/      # Built-in domain
│   │   ├── domain.yaml           # Domain manifest
│   │   ├── schemas/              # Content schemas
│   │   ├── templates/            # SCD/Bundle templates
│   │   ├── validation/           # Validation rules
│   │   └── examples/             # Example bundles
│   └── healthcare/               # Commercial domain
│       ├── domain.yaml
│       ├── schemas/
│       ├── templates/
│       └── validation/
└── registry-cache.json            # Cached registry catalog
```

---

## 3. Registry API Specification

### 3.1 Domain Catalog API

**GET /api/v1/domains**

List all available domains:

```json
{
  "domains": [
    {
      "id": "domain:software-development",
      "name": "Software Development",
      "version": "1.0.0",
      "description": "Structured context for software development projects",
      "license": "open",
      "download_url": "https://registry.scs-commercial.com/downloads/software-development/1.0.0",
      "size_bytes": 524288,
      "checksum": "sha256:abc123...",
      "updated_at": "2025-12-01T00:00:00Z"
    },
    {
      "id": "domain:healthcare",
      "name": "Healthcare",
      "version": "1.0.0",
      "description": "Structured context for healthcare systems",
      "license": "commercial",
      "price_usd": 99.00,
      "price_model": "per_user_monthly",
      "download_url": "https://registry.scs-commercial.com/downloads/healthcare/1.0.0",
      "requires_license": true,
      "size_bytes": 1048576,
      "checksum": "sha256:def456...",
      "updated_at": "2025-12-10T00:00:00Z"
    }
  ]
}
```

**GET /api/v1/domains/{domain-id}**

Get details for a specific domain:

```json
{
  "id": "domain:healthcare",
  "name": "Healthcare",
  "version": "1.0.0",
  "description": "Structured context for healthcare systems, clinical workflows, and patient care",
  "license": "commercial",
  "author": "SCS Commercial",
  "homepage": "https://scs-commercial.com/domains/healthcare",
  "documentation_url": "https://docs.scs-commercial.com/domains/healthcare",
  "requires_license": true,
  "price_usd": 99.00,
  "price_model": "per_user_monthly",
  "features": [
    "Clinical workflow modeling",
    "HIPAA compliance templates",
    "HL7 FHIR integration patterns",
    "Patient care pathway design"
  ],
  "versions": [
    "1.0.0",
    "0.9.0",
    "0.8.0"
  ],
  "dependencies": [],
  "metadata": {
    "tags": ["healthcare", "medical", "clinical"],
    "industry": ["Healthcare", "Medical"],
    "use_cases": ["EHR", "Patient portals", "Telehealth"]
  }
}
```

**GET /api/v1/domains/{domain-id}/versions/{version}**

Get specific version details.

### 3.2 License Verification API

**POST /api/v1/licenses/verify**

Verify a license key:

Request:
```json
{
  "domain_id": "domain:healthcare",
  "license_key": "HC-XXXX-XXXX-XXXX-XXXX",
  "machine_id": "abc123..."
}
```

Response:
```json
{
  "valid": true,
  "domain_id": "domain:healthcare",
  "license_type": "commercial",
  "expires_at": "2026-12-12T00:00:00Z",
  "seats": 5,
  "seats_used": 2,
  "features": ["full"],
  "metadata": {
    "organization": "Acme Healthcare",
    "contact": "admin@acme.com"
  }
}
```

**POST /api/v1/licenses/activate**

Activate a license for a machine:

Request:
```json
{
  "domain_id": "domain:healthcare",
  "license_key": "HC-XXXX-XXXX-XXXX-XXXX",
  "machine_id": "abc123...",
  "user_email": "user@acme.com"
}
```

Response:
```json
{
  "activated": true,
  "domain_id": "domain:healthcare",
  "activation_id": "act_123456",
  "expires_at": "2026-12-12T00:00:00Z"
}
```

### 3.3 Domain Download API

**GET /downloads/{domain-id}/{version}**

Download domain package (requires valid license for commercial domains).

Returns: `.tar.gz` archive containing domain manifest, schemas, templates, etc.

---

## 4. CLI Commands

### 4.1 Domain Discovery

```bash
# List all available domains in registry
scs domain list

# Search for domains by keyword
scs domain search healthcare

# Show domain details
scs domain info healthcare

# List installed domains
scs domain list --installed
```

### 4.2 Domain Installation

```bash
# Install a free domain
scs domain install software-development

# Install a commercial domain (prompts for license key)
scs domain install healthcare

# Install with license key provided
scs domain install healthcare --license-key HC-XXXX-XXXX-XXXX-XXXX

# Install specific version
scs domain install healthcare@1.0.0

# Uninstall a domain
scs domain uninstall healthcare
```

### 4.3 License Management

```bash
# Activate license for a domain
scs domain activate healthcare --license-key HC-XXXX-XXXX-XXXX-XXXX

# Check license status
scs domain licenses

# Deactivate license
scs domain deactivate healthcare
```

### 4.4 Domain Updates

```bash
# Check for domain updates
scs domain check-updates

# Update a specific domain
scs domain update healthcare

# Update all domains
scs domain update --all
```

### 4.5 Domain Selection

```bash
# Set project domain
scs domain set healthcare

# Get current project domain
scs domain current

# Reset to default domain
scs domain set software-development
```

---

## 5. Registry Client Implementation

### 5.1 Registry Client Class

```python
class RegistryClient:
    def __init__(self, registry_url, cache_dir):
        self.registry_url = registry_url
        self.cache_dir = cache_dir
        self.cache = RegistryCache(cache_dir)

    def list_domains(self, refresh=False):
        """List all available domains"""
        if not refresh and self.cache.is_valid():
            return self.cache.get_domains()

        response = requests.get(f"{self.registry_url}/api/v1/domains")
        domains = response.json()["domains"]
        self.cache.save_domains(domains)
        return domains

    def get_domain_info(self, domain_id):
        """Get detailed information about a domain"""
        response = requests.get(f"{self.registry_url}/api/v1/domains/{domain_id}")
        return response.json()

    def download_domain(self, domain_id, version, license_key=None):
        """Download a domain package"""
        headers = {}
        if license_key:
            headers["X-License-Key"] = license_key

        url = f"{self.registry_url}/downloads/{domain_id}/{version}"
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 403:
            raise LicenseRequiredError(f"Domain {domain_id} requires a valid license")

        return response.content

    def verify_license(self, domain_id, license_key):
        """Verify a license key"""
        machine_id = self._get_machine_id()

        response = requests.post(
            f"{self.registry_url}/api/v1/licenses/verify",
            json={
                "domain_id": domain_id,
                "license_key": license_key,
                "machine_id": machine_id
            }
        )

        return response.json()

    def activate_license(self, domain_id, license_key, user_email):
        """Activate a license"""
        machine_id = self._get_machine_id()

        response = requests.post(
            f"{self.registry_url}/api/v1/licenses/activate",
            json={
                "domain_id": domain_id,
                "license_key": license_key,
                "machine_id": machine_id,
                "user_email": user_email
            }
        )

        return response.json()
```

### 5.2 Domain Manager Class

```python
class DomainManager:
    def __init__(self, domains_dir, registry_client):
        self.domains_dir = domains_dir
        self.registry = registry_client

    def install_domain(self, domain_id, version=None, license_key=None):
        """Install a domain from the registry"""
        # Get domain info
        info = self.registry.get_domain_info(domain_id)
        version = version or info["version"]

        # Verify license if commercial
        if info["requires_license"]:
            if not license_key:
                raise LicenseRequiredError(f"Domain {domain_id} requires a license key")

            license_info = self.registry.verify_license(domain_id, license_key)
            if not license_info["valid"]:
                raise InvalidLicenseError("Invalid or expired license")

        # Download domain package
        package = self.registry.download_domain(domain_id, version, license_key)

        # Extract to domains directory
        domain_path = os.path.join(self.domains_dir, domain_id.replace("domain:", ""))
        extract_package(package, domain_path)

        # Validate domain manifest
        manifest = self._load_domain_manifest(domain_path)
        self._validate_domain_manifest(manifest)

        # Save license if commercial
        if license_key:
            self._save_license(domain_id, license_key)

        print(f"✓ Domain {domain_id} version {version} installed successfully")

    def list_installed_domains(self):
        """List all installed domains"""
        domains = []
        for domain_dir in os.listdir(self.domains_dir):
            manifest_path = os.path.join(self.domains_dir, domain_dir, "domain.yaml")
            if os.path.exists(manifest_path):
                manifest = self._load_domain_manifest(manifest_path)
                domains.append(manifest)
        return domains

    def get_domain(self, domain_id):
        """Load a domain by ID"""
        domain_name = domain_id.replace("domain:", "")
        domain_path = os.path.join(self.domains_dir, domain_name)

        if not os.path.exists(domain_path):
            raise DomainNotFoundError(f"Domain {domain_id} is not installed")

        return Domain.load(domain_path)
```

---

## 6. Offline Support

### 6.1 Local Domain Installation

Users can install domains from local files:

```bash
# Install domain from local directory
scs domain install ./my-custom-domain/

# Install domain from package file
scs domain install ./healthcare-domain-1.0.0.tar.gz
```

### 6.2 Offline License Activation

For offline environments:

```bash
# Generate activation request
scs domain activate healthcare --offline > activation-request.json

# (User sends request to vendor, receives activation-response.json)

# Apply activation response
scs domain activate healthcare --offline-response activation-response.json
```

---

## 7. Security Considerations

### 7.1 Package Verification

- All domain packages include SHA256 checksums
- Packages are verified before installation
- Manifests are validated against schema

### 7.2 License Protection

- License keys are stored encrypted in `~/.scs/licenses/`
- Machine ID ensures licenses can't be freely shared
- License verification happens on domain load (not just install)

### 7.3 Registry Communication

- All registry communication uses HTTPS
- API tokens for authenticated requests
- Rate limiting to prevent abuse

---

## 8. Integration Points

### 8.1 Existing Registry Project

Questions for integration with your existing registry:

1. **Registry API format**: Does your registry already have an API? What format?
2. **Domain storage**: How are domains currently stored/distributed?
3. **License management**: Is there existing license verification infrastructure?
4. **Hosting**: Self-hosted or cloud-based registry?

### 8.2 Migration Path

If existing registry is different:

- Create adapter layer to translate between formats
- Maintain backwards compatibility
- Gradual migration strategy

---

## 9. Open Questions

1. **Registry hosting**: Where will the production registry be hosted?
2. **CDN for domains**: Should domain downloads use CDN for performance?
3. **Domain updates**: How to handle breaking changes in domain schemas?
4. **Private registries**: Should organizations be able to run private registries?
5. **Domain marketplace**: Will third parties be able to publish domains?

---

## 10. Next Steps

1. Review existing registry project architecture
2. Define registry API contract
3. Implement registry client library
4. Implement domain manager
5. Create test registry with sample domains
6. Integrate with CLI commands

---

*This design assumes integration with an external registry service. Specific implementation details may vary based on the existing registry project architecture.*
