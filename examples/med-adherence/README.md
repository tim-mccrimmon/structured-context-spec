# Medication Adherence System — Project Bundle Example

A **Project bundle** for a healthcare application, organized by concept. It shows how a
project carries its own governance context in SCS 0.6.0, independently of any
organization-wide Domain bundle.

## Structure

```
examples/med-adherence/
├── project-bundle.yaml        # Project bundle: imports the project's concept bundles
├── concepts/                  # 11 concept bundles (architecture, security, ...)
└── scds/project/              # Project-tier SCDs referenced by the concept bundles
```

## How It Fits the 0.6.0 Model

- **Project bundle** (`project-bundle.yaml`) imports 11 concept bundles. A project bundle
  may instead list its project-tier SCDs directly; it does one or the other, not both.
- **No meta, standards, or domain imports.** Organization-wide rules live in the
  organization's Domain bundle, which is authored and versioned separately. A runtime
  applies the Domain bundle and this Project bundle side by side.
- **Standards are cited, not bundled.** `hipaa-compliance.yaml` and `soc2-controls.yaml`
  carry `cites:` entries such as `std:hipaa#164.312`. See `spec/0.6/citations.md`.

Earlier versions of this example imported `bundle:meta`, `bundle:standards`, and a
`bundle:software-development` domain bundle. Those imports were removed in 0.6.0
(`docs/MIGRATION-0.6.0.md`).

## About the Example Project

**Medication Adherence System**
- Healthcare application helping patients track medication schedules
- Sends medication reminders via mobile app and SMS
- Provides adherence insights to healthcare providers
- Subject to HIPAA and SOC 2

## Validation

```bash
scs-validate --bundle examples/med-adherence/project-bundle.yaml
```

The validator resolves every import and SCD in the tree and checks that the project
bundle imports only concept bundles.

## Related Documentation

- [Bundle Format Specification](../../spec/0.6/bundle-format.md)
- [Standard Citations](../../spec/0.6/citations.md)
- [Bundle Lifecycle](../../docs/bundle-lifecycle.md)
