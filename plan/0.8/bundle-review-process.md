# Plan: Bundle Review Process

- **Status**: Draft (2026-11-07). Planning only; nothing built.
- **Brief**: kept privately with the maintainer (contains customer material).
- **Related**: `spec/0.7/bundle-format.md` §7.6 (content digest), `spec/0.7/runtime-artifact.md`
  (`source_digest`), `schema/bundles/scd-bundle-schema.json` (`version_approved_by`)

## Goal

Non-technical leaders review a bundle in readable form, direct changes, route it from person to
person, and certify it as a compliance step in the organization's quality management system
(QMS). Agents only receive content whose digest matches a certified version.

## Approach

- **Context repository**: content and history. Reviewers never see it.
- **Review package**: self-contained HTML rendered from one versioned bundle at one digest.
  Every rule verbatim with its id, inherited Domain rules marked, digest on the cover.
- **QMS**: routes the change order, carries review comments and rejections, records the
  certification. The QMS is the system of record for approval.
- **Change loop**: a reviewer rejects with comments; the bundle author applies them with the
  update skill; a new digest and package go back through the change order.
- **Approval record**: committed beside the bundle, naming the QMS record and the certified
  digest. A check refuses release when they do not match.

## Design constraint: approval cannot live in the manifest

`version_approved_by` / `version_approved_at` are in the bundle manifest, and the manifest is
part of the content digest (§7.6). Certification happens after the package is generated, so
writing it into the manifest would change the digest that was certified. The certification
needs its own record beside the bundle, as the version manifest already is.

## Phases

### Phase 0: Prepare

- Test bundle: the Domain and Project versioned during 0.7 acceptance (WP-13 Test 2). It
  contains customer material, so packages are generated and viewed on the test machine and
  stay out of this repository.
- Requirements recorded in the brief; non-goals revised.
- Question list for the QMS vendor (below).
- **Exit**: brief updated, questions ready.

### Phase 1: Review package generator

- `scs view` in `tools/cli`: one versioned bundle in, one self-contained HTML file out (no
  external assets, so it can be attached to a QMS record).
  - Cover: bundle name, version, `source_digest` and whether it matches, approver, release
    date. No generation date, so the same release always produces the same file.
  - Overview: summary, then tree Bundle → concepts (owner) → SCDs (counts).
  - SCD sections: prohibitions, directives and facts verbatim with ids; compiled lines;
    `cites`, `derived_from`; relationships as links.
  - Project packages: inherited Domain as a marked branch.
  - The summary is mechanical (counts and structure), not AI-written, so the same digest always
    produces the same package. AI explanation stays in the Claude session.
- Skill: folded into `scs-explain` (review package section) rather than a fifth skill.
- **Exit**: the test bundle's package is readable by a non-technical reviewer; two runs from
  the same digest produce identical output.

### Phase 2: Approval record and check

- Approval record beside the version manifest: bundle reference, digest, system of record,
  record id, decision, approvers (role, date), package checksum.
- `scs bundle verify-approval` (name TBD): fails on digest mismatch or missing record; usable
  in CI to gate release.
- Decide the meaning of in-manifest `version_approved_by` alongside the external record:
  author sign-off, or deprecated in favor of the record.
- **Exit**: a hand-written record for the test bundle passes; changing one rule fails it.

### Phase 3: Manual round trip in a QMS sandbox

- Attach the package to a change order, route to two or three test approvers, reject once
  with comments, apply changes with the update skill, regenerate, reroute, certify.
- Record the change-order id in the approval record by hand; run the check.
- Log friction: QMS configuration needed, how comments come back, HTML rendering.
- **Exit**: one complete round trip; friction logged. This is the example shown to the QMS
  administrators.

### Phase 4: Review with the customer

- Walk through the sandbox round trip.
- Decide: production QMS configuration and its own change control, who the bundle author is,
  approver roles and order, whether certification is the organization's Part 11 signature for
  this record.
- **Exit**: process agreed; production configuration requested.

### Phase 5: Spec (RFC for 0.8, parallel with phases 2-4)

- Effective context view shape, and an approval record that references an external system of
  record. No vendor specifics in the spec.
- Drafted from what phases 1-3 needed.

### Phase 6: Automation (once the QMS API is available)

- Create the change order and attach the package; read status and signatures back; write the
  approval record from them.
- Home decided in phase 4: customer engagement work or an SCP connector.

## Questions for the QMS vendor

- Document type and change-order workflow for an AI context bundle: exists or needs
  configuring?
- Can HTML be attached and viewed in the browser, or PDF only?
- How do reviewer comments and rejections come back? Exportable?
- Approver order, roles, and signature meaning.
- API: create change order, attach file, read status, read signature and audit records; auth.
- Does a change to QMS configuration go through the organization's change control?

## Open decisions

- Package format: HTML assumed; confirm in phase 3.
- `version_approved_by` meaning (phase 2).
- Command and record file names.
