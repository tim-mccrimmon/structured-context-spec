# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the Structured Context Specification or related tooling, please report it responsibly.

**Contact:** tim@ohanaconsulting.llc

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if applicable)

**Response time:** We will respond within 48 hours and work with you to understand and address the issue.

## Supported Versions

SCS is currently in active development (v0.x). Security updates will be applied to:
- Current version (v0.3.0)
- Previous minor version (if applicable)

Once we reach v1.0, we will maintain security updates for all minor versions of the current major release.

## Security Considerations

While SCS is a specification and tooling for managing structured context, please be aware:

- **Context as Code:** Structured context documents may contain sensitive organizational information. Handle them with the same security practices as source code.
- **Validation:** Always validate bundles and SCDs before deployment, especially if importing from external sources.
- **Access Control:** If using SCS in production, apply appropriate access controls to your context repositories.

## Scope

This security policy covers:
- The SCS specification (vulnerabilities in the spec itself)
- Reference implementations (validator, CLI tools)
- Schemas and templates

For security issues in third-party implementations or commercial products built on SCS (like OICP), please contact those vendors directly.

---

Thank you for helping keep SCS and the community safe!
