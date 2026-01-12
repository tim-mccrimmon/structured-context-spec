# Building scs-med-adherence: A Step-by-Step Guide

**Project**: Medication Adherence Tracking Application
**Project Type**: Healthcare (HIPAA, CHAI, TEFCA compliant)
**Purpose**: Test the scs-tools CLI as a new user building a reference implementation

---

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] `scs-tools` installed (`pip install -e .` from scs-cli directory)
- [ ] `scs-validator` installed (`pip install -e .` from scs-spec/tools/scd-validator)
- [ ] A working directory where you want to create the project

Verify installation:
```bash
scs --version
scs --help
```

---

## Step 1: Create the Project

Navigate to your projects directory and create the new project:

```bash
# Navigate to where you want to create the project
cd ~/projects  # or wherever you keep your projects

# Create the healthcare project
scs new project scs-med-adherence \
  --type healthcare \
  --author "Your Name" \
  --email "your.email@example.com"
```

**Expected Output:**
- Project created at `./scs-med-adherence`
- Directory structure with bundles/, context/, docs/, .scs/
- All 10 domain bundles created
- ~38 SCD templates generated
- Healthcare-specific SCDs included (HIPAA, CHAI, TEFCA)

**Verify:**
```bash
cd scs-med-adherence
ls -la
# Should see: bundles/, context/, docs/, .scs/, README.md, VERSION, .gitignore
```

---

## Step 2: Explore the Generated Structure

### 2.1 Review Project Structure

```bash
# View the complete directory tree
tree -L 3

# Or manually explore:
ls -la bundles/
ls -la bundles/domains/
ls -la context/project/
```

**Expected Structure:**
```
scs-med-adherence/
├── bundles/
│   ├── project-bundle.yaml      # Top-level bundle
│   ├── meta-bundle.yaml          # Meta vocabulary
│   ├── standards-bundle.yaml     # Compliance standards
│   └── domains/                  # Domain bundles
│       ├── architecture.yaml
│       ├── security.yaml
│       ├── compliance-governance.yaml
│       └── ... (7 more)
├── context/
│   └── project/                  # Project-tier SCDs
│       ├── system-context.yaml
│       ├── tech-stack.yaml
│       ├── hipaa-compliance.yaml
│       ├── chai-adherence.yaml
│       ├── tefca-participation.yaml
│       └── ... (30+ more)
├── docs/
│   └── GETTING_STARTED.md
├── .scs/
│   └── config
├── .gitignore
├── README.md
└── VERSION
```

### 2.2 Review Key Files

```bash
# Check project configuration
cat .scs/config

# Review project README
cat README.md

# Check getting started guide
cat docs/GETTING_STARTED.md

# Review project bundle (references all domain bundles)
cat bundles/project-bundle.yaml
```

---

## Step 3: Validate the Initial Project

Before making any changes, validate that the generated project is correct:

```bash
# Validate the entire project bundle
scs validate --bundle bundles/project-bundle.yaml

# Or use the shortcut
scs bundle validate

# Validate with verbose output to see what's being checked
scs validate --bundle bundles/project-bundle.yaml --verbose

# Validate in strict mode (fail on warnings)
scs validate --bundle bundles/project-bundle.yaml --strict
```

**Expected Output:**
- All syntax validation should pass
- Schema validation should pass
- May have warnings about placeholder content (this is expected)

**If validation fails:**
- Note the specific errors
- Check if it's a template issue or validator issue
- Document for bug fixes

---

## Step 4: Customize for Medication Adherence

Now customize the SCDs for the actual medication adherence application.

### 4.1 Define System Context

```bash
# Edit the system context SCD
vim context/project/system-context.yaml
# or use your preferred editor
code context/project/system-context.yaml
```

**What to customize:**
- `system_name`: "Medication Adherence Tracker"
- `system_purpose`: Describe the medication adherence tracking system
- `system_boundaries`: What's in scope (patient medication tracking, reminders, adherence reports) and out of scope (prescription fulfillment, insurance billing)
- `external_actors`: Patients, caregivers, healthcare providers
- `external_systems`: EHR systems, pharmacy systems, notification services
- `key_data_flows`: Prescription ingestion, reminder generation, adherence reporting

### 4.2 Define Tech Stack

```bash
# Edit tech stack
vim context/project/tech-stack.yaml
```

**What to define:**
- Backend: Python/FastAPI, Node.js/Express, etc.
- Frontend: React, React Native for mobile
- Database: PostgreSQL, MongoDB, etc.
- Cloud: AWS, GCP, Azure
- Key libraries and frameworks

### 4.3 Define Security & Compliance

```bash
# Edit authentication/authorization
vim context/project/authn-authz.yaml

# Edit data protection
vim context/project/data-protection.yaml

# Edit HIPAA compliance
vim context/project/hipaa-compliance.yaml

# Edit CHAI adherence
vim context/project/chai-adherence.yaml
```

**Key areas to address:**
- How PHI is protected
- Encryption at rest and in transit
- Access controls (patient-level data isolation)
- Audit logging for compliance
- HIPAA minimum necessary standard
- CHAI principles (consent, transparency, security)

### 4.4 Define Data Model

```bash
# Edit data model
vim context/project/data-model.yaml
```

**Define entities:**
- Patient
- Medication
- MedicationSchedule
- AdherenceRecord
- Reminder
- CaregiverRelationship

---

## Step 5: Add Additional SCDs (if needed)

If you need SCDs that weren't generated by default:

```bash
# Add a specific SCD
scs add scd <scd-name>

# Example: If you need to add more custom SCDs
scs add scd api-specifications
scs add scd database-schema
```

List available SCD templates:
```bash
ls scs_tools/templates/scds/
```

---

## Step 6: Manage Bundles

### 6.1 List Project Bundles

```bash
# List bundles in your project
scs bundle list

# List all available bundle templates
scs bundle list --available
```

### 6.2 View Bundle Details

```bash
# Get detailed info about a specific bundle
scs bundle info architecture
scs bundle info security
scs bundle info compliance-governance
```

### 6.3 Add Missing Bundles (if needed)

```bash
# Add a domain bundle that's missing
scs add bundle <bundle-name>

# Example:
scs add bundle data-provenance
```

---

## Step 7: Validate After Customization

After making changes, validate again:

```bash
# Validate the entire project
scs bundle validate

# Validate specific SCDs
scs validate context/project/system-context.yaml
scs validate context/project/tech-stack.yaml

# Validate with JSON output for CI/CD
scs validate --bundle bundles/project-bundle.yaml --output json

# Check for any warnings
scs validate --bundle bundles/project-bundle.yaml --strict
```

**Fix any issues:**
- Invalid YAML syntax
- Missing required fields
- Type/tier mismatches
- Invalid semver versions
- Incomplete provenance

---

## Step 8: Initialize Git Repository

```bash
# Initialize git (if not already done)
git init

# Review what will be committed
git status

# Add all files
git add .

# Create initial commit
git commit -m "Initial SCS project structure for medication adherence tracker

- Generated with scs-tools v0.1.0
- Healthcare project type (HIPAA, CHAI, TEFCA)
- 10 domain bundles with 38 SCDs
- Customized for medication adherence tracking

Co-Authored-By: SCS-Tools <noreply@scs.dev>"

# Add remote and push
git remote add origin <your-repo-url>
git push -u origin main
```

---

## Step 9: Start Development

### 9.1 Review Documentation

```bash
# Read getting started guide
cat docs/GETTING_STARTED.md

# Review project README
cat README.md
```

### 9.2 Set Up Development Environment

Based on your tech stack definitions:

1. Create virtual environment (Python) or install dependencies (Node.js)
2. Set up database
3. Configure environment variables
4. Set up development secrets (not committed to git)

### 9.3 Implement Core Features

Use the SCDs as your implementation guide:
- Reference `system-context.yaml` for system boundaries
- Reference `component-model.yaml` for architecture
- Reference `integration-map.yaml` for external integrations
- Reference `data-model.yaml` for database schema
- Reference compliance SCDs for security requirements

---

## Step 10: Test the Workflow

### Things to Test and Document:

#### ✅ Project Creation
- [ ] Project created successfully with correct structure
- [ ] All expected files generated
- [ ] Healthcare-specific SCDs included
- [ ] File permissions correct

#### ✅ Validation
- [ ] Initial validation passes (or expected warnings only)
- [ ] Validation catches syntax errors
- [ ] Validation catches schema violations
- [ ] Strict mode works as expected

#### ✅ Bundle Management
- [ ] Can list bundles
- [ ] Can view bundle info
- [ ] Bundle references are correct
- [ ] All domain bundles present

#### ✅ Customization
- [ ] Can edit SCDs without breaking validation
- [ ] Templates have good placeholders
- [ ] Examples are clear and helpful
- [ ] Jinja2 variables properly substituted

#### ✅ Additional Operations
- [ ] Can add individual SCDs
- [ ] Can add bundles
- [ ] Git workflow works smoothly
- [ ] Documentation is accurate

---

## Common Issues & Troubleshooting

### Issue: Validation fails with schema errors
**Solution:**
```bash
# Check which schema is failing
scs validate --bundle bundles/project-bundle.yaml --verbose

# Verify schema directory is accessible
ls -la ~/path/to/scs-spec/schema/
```

### Issue: Can't find SCD templates
**Solution:**
```bash
# List available templates
ls $(python -c "from scs_tools.utils.files import get_template_path; print(get_template_path())")/scds/

# Or check installation
pip show scs-tools
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall in editable mode
cd /path/to/scs-cli
pip install -e .

# Verify installation
python -c "import scs_tools; print(scs_tools.__version__)"
```

---

## Success Criteria

At the end of this exercise, you should have:

1. ✅ A complete SCS project structure for medication adherence
2. ✅ All healthcare compliance SCDs (HIPAA, CHAI, TEFCA)
3. ✅ Customized SCDs describing the actual system
4. ✅ Valid project bundle that passes validation
5. ✅ Git repository with initial commit
6. ✅ Documentation of any issues or improvements needed
7. ✅ Confidence that a new user could follow this process

---

## Feedback & Improvements

As you go through this process, document:

### What Worked Well
- List features that worked smoothly
- Commands that were intuitive
- Generated content that was helpful

### What Needs Improvement
- Confusing error messages
- Missing documentation
- Template improvements needed
- Command usability issues
- Validation false positives/negatives

### Feature Requests
- Missing commands
- Additional templates needed
- Better error handling
- Improved output formatting

---

## Next Steps After Completion

Once you've successfully created and validated the project:

1. **Start implementation**: Use the SCDs as implementation guides
2. **CI/CD integration**: Add `scs validate` to your CI pipeline
3. **Team onboarding**: Use this guide to onboard team members
4. **Iterate on SCDs**: Update as requirements evolve
5. **Share feedback**: Document learnings for tool improvement

---

## Quick Reference Commands

```bash
# Create project
scs new project <name> --type healthcare --author "Name" --email "email"

# Validate
scs validate --bundle bundles/project-bundle.yaml
scs bundle validate

# List bundles
scs bundle list
scs bundle list --available

# Add SCD/bundle
scs add scd <scd-name>
scs add bundle <bundle-name>

# Bundle info
scs bundle info <bundle-name>

# Initialize in existing project
scs init --type healthcare
```

---

## Notes & Observations

Use this section to capture notes as you work through the process:

```
Date: YYYY-MM-DD
Time: HH:MM

[Your observations here]

Issues encountered:
-

Things that worked well:
-

Questions raised:
-

Improvements needed:
-
```

---

**Good luck with your reference implementation!** 🚀

Remember: The goal is to stress-test the tools as a real user would. Document everything - both successes and friction points. This feedback is invaluable for improving scs-tools.
