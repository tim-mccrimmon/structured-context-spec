# GitHub Repository Setup Checklist

**Repository:** structured-context-spec
**Owner:** tim-mccrimmon
**Status:** Pre-launch review

---

## ✅ COMPLETED

### Repository Files
- [x] README.md - Comprehensive, well-formatted
- [x] LICENSE - Apache 2.0
- [x] CONTRIBUTING.md - Detailed contribution guidelines
- [x] .gitignore - Properly configured
- [x] Issue templates (4 templates: bug, feature, proposal, question)

---

## 🔧 NEEDS CONFIGURATION (On GitHub.com)

### Repository Settings (github.com/tim-mccrimmon/structured-context-spec/settings)

#### About Section
- [ ] **Description:** "A community-driven specification for creating, validating, and versioning structured context for AI systems"
- [ ] **Website:** https://structuredcontext.dev
- [ ] **Topics/Tags:** Add these topics:
  - `ai`
  - `context-management`
  - `specification`
  - `yaml`
  - `open-source`
  - `agent-context`
  - `structured-context`
  - `scs`

#### Features (Settings → General)
- [ ] **Wikis:** Disabled (use docs/ directory instead)
- [ ] **Issues:** Enabled ✓
- [ ] **Sponsorships:** Disabled (for now)
- [ ] **Discussions:** **ENABLE THIS** ← Important for community
- [ ] **Projects:** Disabled (for now)
- [ ] **Preserve this repository:** Disabled (for now)

#### Social Preview Image
- [ ] Upload custom image (1280x640px)
  - Suggestion: Simple graphic with "SCS" logo + tagline
  - Can create in Canva (5 minutes)

---

## 📋 OPTIONAL (But Recommended)

### Additional Files (Create these if time permits)

#### SECURITY.md
**Location:** Root directory
**Purpose:** Security vulnerability reporting instructions
**Priority:** Medium (good practice for v1.0)

```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in SCS, please email:
tim@ohanaconsulting.llc

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours.

## Supported Versions

Currently, all versions of SCS are in active development (v0.x).
Security updates will be backported to recent minor versions.
```

#### Pull Request Template
**Location:** `.github/pull_request_template.md`
**Purpose:** Guide contributors on PR format
**Priority:** Low (can add after launch)

```markdown
## Description
Brief description of changes

## Related Issue
Closes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] I have read CONTRIBUTING.md
- [ ] My code follows the style guidelines
- [ ] I have added tests (if applicable)
- [ ] Documentation has been updated
```

#### GitHub Actions (Automation)
**Location:** `.github/workflows/`
**Purpose:** Automated validation, testing
**Priority:** Low (nice-to-have, not critical)

**Potential workflows:**
- Validate YAML files on PR
- Check links in markdown
- Run validator tests
- Auto-label issues

---

## 🎯 HIGH PRIORITY (Do Before Launch)

### Must-Do on GitHub.com (10 minutes):

1. **Go to:** https://github.com/tim-mccrimmon/structured-context-spec

2. **Click "About" gear icon** (top right of Code tab)
   - Add description
   - Add website URL
   - Add topics (8 topics listed above)
   - Check "Include in the home page"

3. **Enable Discussions:**
   - Settings → General → Features
   - Check "Discussions"
   - Initialize with Welcome category

4. **Verify Settings:**
   - Settings → General → Features
   - Issues: Enabled ✓
   - Wiki: Disabled ✓
   - Projects: Disabled ✓

---

## 🎨 NICE-TO-HAVE (Post-Launch)

### Social Preview Image
Create 1280x640px image in Canva:
- SCS logo/text
- Tagline: "Version control for AI agent context"
- Clean, professional design
- Upload via Settings → Social preview

### Pin Important Issues
After launch, pin:
- "Welcome! Start here" issue
- "Roadmap to v1.0" issue
- "Community feedback thread"

### GitHub Labels
Default labels are fine for now, but consider adding:
- `good-first-issue` (already exists)
- `help-wanted` (already exists)
- `spec-change` (custom)
- `breaking-change` (custom)
- `needs-rfc` (custom)

Can add these via Settings → Issues → Labels

---

## ⚠️ COMMON MISTAKES TO AVOID

- [ ] Don't enable Wiki (creates documentation split)
- [ ] Don't enable Projects (adds complexity too early)
- [ ] Don't add too many labels initially (can add as needed)
- [ ] Don't worry about GitHub Actions yet (premature optimization)

---

## 📊 POST-LAUNCH MONITORING

### Week 1:
- Watch for first issues/PRs
- Monitor Discussions activity
- Check star count growth
- Review traffic in Insights

### Week 2:
- Add pinned issues if needed
- Review label usage
- Consider GitHub Actions if manual work is high
- Update topics if needed

---

## ✅ FINAL PRE-LAUNCH CHECK

**Before posting to HN/Reddit/LinkedIn:**

1. [ ] Visit repo URL: https://github.com/tim-mccrimmon/structured-context-spec
2. [ ] Description visible under repo name? ✓
3. [ ] Website link visible? ✓
4. [ ] Topics/tags visible? ✓
5. [ ] Discussions tab visible? ✓
6. [ ] README loads correctly? ✓
7. [ ] Issue templates work? (Test by clicking "New Issue") ✓

**If all checked, you're ready to launch!** 🚀

---

**Last Updated:** 2026-01-09
**Next Review:** Post-launch (Jan 20)
