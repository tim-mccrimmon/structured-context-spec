# SCS CLI Examples

This directory contains references to complete, working examples of SCS projects created with the CLI.

Rather than duplicating entire projects here, we maintain separate example repositories that demonstrate real-world usage of the SCS CLI.

---

## Example Projects

### 1. Medication Adherence Tracker

**Repository**: [scs-example-med-adherence](https://github.com/tim-mccrimmon/scs-example-med-adherence)

**Description**: A complete healthcare application for tracking patient medication adherence, built entirely using the SCS CLI.

**What It Demonstrates**:
- Healthcare project type (HIPAA, CHAI, TEFCA compliance)
- Complete SCD documentation workflow
- Mobile app architecture (patient-facing)
- EHR system integration
- Compliance documentation best practices
- All 11 domain bundles fully populated

**Project Type**: Healthcare

**Key Features**:
- 38+ SCDs with realistic, production-ready content
- HIPAA compliance controls documented
- CHAI adherence principles implemented
- TEFCA participation requirements
- Complete data model for medication tracking
- Security and privacy controls
- Integration architecture

**How It Was Created**:
```bash
scs new project scs-example-med-adherence --type healthcare --author "SCS Team"
# Then customized all SCDs with real content
scs bundle validate
```

**Using This Example**:

Clone and explore:
```bash
git clone https://github.com/tim-mccrimmon/scs-example-med-adherence.git
cd scs-example-med-adherence

# Browse bundles/ and context/ directories
cat context/project/system-context.yaml
cat context/project/hipaa-compliance.yaml
```

As a starting point:
```bash
git clone https://github.com/tim-mccrimmon/scs-example-med-adherence.git my-medication-app
cd my-medication-app
# Customize for your needs
scs bundle validate
```

---

### 2. CHAI Adherence Framework (`chai-adherence`)

**Repository**: *(Coming soon)*

**Description**: A focused example demonstrating CHAI (Consumer Health Application Interface) compliance principles.

**What It Demonstrates**:
- CHAI framework implementation
- Consumer health app requirements
- Consent management
- Transparency and disclosure requirements
- Patient rights implementation

**Project Type**: Healthcare

*(Details to be added when example is complete)*

---

## Why External Example Repositories?

We maintain examples as separate repositories rather than subdirectories because:

1. **Real-World Usage** - Shows how actual projects are structured
2. **Independent Evolution** - Examples can grow and evolve independently
3. **Full Git History** - Users can see the development process
4. **Lean CLI Repo** - Keeps this repository focused on the CLI tool
5. **Easy Forking** - Users can fork entire example projects
6. **Realistic Scale** - Examples can be as detailed as needed

---

## Creating Your Own Example

Have you built a great SCS project? Share it with the community!

### Example Project Checklist

Your example should:
- ✅ Be generated using `scs new project` (document the command)
- ✅ Have all SCDs filled in with realistic content (no placeholders)
- ✅ Pass `scs bundle validate` successfully
- ✅ Include a descriptive README.md explaining the project
- ✅ Represent a real-world use case
- ✅ Demonstrate best practices
- ✅ Include the CLI version used to generate it

### Submitting Your Example

1. Create your SCS project in its own repository
2. Document how it was created (commands used)
3. Add a comprehensive README
4. Submit a PR to add a reference here

---

## Validating Examples

To validate any example project:

```bash
cd /path/to/example-project
scs validate --bundle bundles/project-bundle.yaml
```

Or use the shortcut:

```bash
cd /path/to/example-project
scs bundle validate
```

---

## Example Project Types

Examples covering different project types:

- **Healthcare**: ✅ [Medication Adherence Tracker](https://github.com/tim-mccrimmon/scs-example-med-adherence)
- **Fintech**: *(Coming soon)*
- **SaaS**: *(Coming soon)*
- **Government**: *(Coming soon)*
- **Minimal**: *(Coming soon)*
- **Standard**: *(Coming soon)*

---

## Additional Resources

- **Tutorial**: See `scs-med-adherence.md` in the root of this repo for a step-by-step guide
- **Documentation**: Check the [main README](../README.md) for CLI usage
- **Templates**: Browse `scs_tools/templates/` to see available SCD and bundle templates
- **Help**: Run `scs --help` for command reference

---

## Questions?

- Open an issue if you have questions about examples
- Check the main README for CLI documentation
- Review existing examples for patterns and best practices
