# Contributing to Structured Context Specification (SCS)

Thank you for your interest in contributing to SCS! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

---

## Code of Conduct

This project adheres to a code of conduct adapted from the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code. Please report unacceptable behavior to [tim@ohana-tech.com](mailto:tim@ohana-tech.com).

**Our Standards:**
- Be respectful and inclusive
- Welcome newcomers and help them get oriented
- Focus on what is best for the community and the specification
- Show empathy towards other community members
- Accept constructive criticism gracefully

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. actual behavior
- **Environment details** (OS, Python version, validator version)
- **Example files** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear use case** - why is this enhancement needed?
- **Detailed description** of the proposed functionality
- **Examples** of how it would work
- **Alternatives considered**

### Contributing to Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos or clarifying confusing sections
- Adding examples or use cases
- Writing guides or tutorials
- Improving API documentation
- Translating documentation

### Contributing to the Specification

The SCS specification is the core of this project. Contributions might include:

- Clarifying ambiguous language
- Adding missing definitions
- Proposing new bundle types or SCD tiers
- Suggesting validation rules
- Providing real-world examples

**Note:** Specification changes require broad consensus and should be discussed in GitHub Issues or Discussions before submitting a PR.

### Contributing Code

Code contributions to the validator, schemas, or tooling are welcome. Areas include:

- Bug fixes in the validator
- New validation rules
- Performance improvements
- Test coverage
- Schema enhancements
- CLI improvements

---

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/structured-context-spec.git
   cd structured-context-spec
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/tim-mccrimmon/structured-context-spec.git
   ```

4. **Set up the validator** (if working on validator code):
   ```bash
   cd tools/scd-validator
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

5. **Run tests** (when available):
   ```bash
   pytest tests/
   ```

### Project Structure

```
structured-context-spec/
├── spec/              # Specification documents
├── schema/            # JSON schemas
├── tools/             # Validator and other tools
│   └── scd-validator/ # Python validator
├── templates/         # SCD and bundle templates
├── examples/          # Working examples
├── docs/              # Documentation and guides
└── rfcs/              # Request for Comments (proposed changes)
```

---

## Submitting Changes

### Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the style guidelines (see below)
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   Commit message format:
   - Use present tense ("Add feature" not "Added feature")
   - Use imperative mood ("Fix bug" not "Fixes bug")
   - Reference issues and PRs liberally
   - First line: brief summary (50 chars or less)
   - Blank line, then detailed explanation if needed

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference related issues
   - Explain what changes were made and why
   - Include examples or screenshots if applicable

6. **Respond to review feedback**:
   - Be open to suggestions
   - Make requested changes promptly
   - Ask questions if feedback is unclear

### PR Review Criteria

Pull requests will be reviewed for:

- **Correctness** - Does it work as intended?
- **Completeness** - Is documentation updated? Are tests included?
- **Clarity** - Is the code/spec clear and well-explained?
- **Consistency** - Does it follow existing patterns and style?
- **Impact** - Does it break existing functionality?

---

## Style Guidelines

### Specification Documents

- Use **Markdown** for all specification documents
- Follow existing document structure and formatting
- Use clear, precise language
- Define new terms in the terminology document
- Provide examples for complex concepts
- Use proper headings hierarchy (##, ###, ####)
- Keep line length reasonable (80-100 characters for readability)

### Python Code (Validator)

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Write **docstrings** for all public functions/classes
- Keep functions focused and concise
- Use meaningful variable and function names
- Add comments for complex logic
- Format code with `black` (if configured)
- Sort imports with `isort` (if configured)

### YAML Files (Schemas, Templates, Examples)

- Use **2 spaces** for indentation (not tabs)
- Follow existing field ordering conventions
- Include inline comments for clarity
- Validate against schemas before committing
- Use meaningful IDs and titles
- Follow SCS naming conventions

### Documentation

- Use **clear, accessible language**
- Provide **examples** wherever possible
- Link to related documentation
- Keep guides task-oriented
- Update table of contents when adding sections
- Use code blocks with language tags

---

## Proposing Major Changes (RFCs)

For significant changes to the specification, consider writing an RFC (Request for Comments):

1. Copy `rfcs/0000-template.md` to `rfcs/NNNN-your-feature.md`
2. Fill out the template with your proposal
3. Submit as a PR for discussion
4. Iterate based on feedback
5. Once accepted, implement the changes

RFCs are appropriate for:
- New bundle types or SCD tiers
- Changes to validation semantics
- New architectural patterns
- Breaking changes

---

## Community

### Getting Help

- **GitHub Discussions** - Ask questions, share ideas, discuss use cases
- **GitHub Issues** - Report bugs or request features
- **Email** - [tim@ohana-tech.com](mailto:tim@ohana-tech.com) for private inquiries

### Staying Informed

- Watch the repository for updates
- Check the CHANGELOG for version history
- Review closed issues and PRs for context

---

## Recognition

Contributors will be recognized in:
- The project README (for significant contributions)
- Release notes
- Git commit history

---

## License

By contributing to SCS, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.

---

## Questions?

Don't hesitate to ask! Open an issue or discussion if anything is unclear. We're here to help new contributors get started.

Thank you for contributing to Structured Context Specification! 🚀
