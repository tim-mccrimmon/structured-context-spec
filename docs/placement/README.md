---
checked: 2026-10-28
---

# SCS Placement Guide

**Provisional (0.7).** This guide is expected to change in the next release, based on testing
with 0.7.

This guide suggests where to put a compiled SCS runtime artifact for some common AI services. It
is advisory and non-normative. RFC 0002 section 10 asks for it, and it sits outside the spec text
because these services change often. Each page lists the date its claims were checked against the
vendor's documentation. Check the linked docs again before relying on a page much later than
that date.

SCS ends at the versioned bundle and its compiled artifact
([runtime-artifact.md](../../spec/0.7/runtime-artifact.md)). Placing or transforming the
artifact is your decision. SCS tools do not do it.

## Two artifacts, two places

There are two kinds of artifact:

- A **Domain** artifact governs all of an owner's work. The owner can be an organization or one
  person.
- A **Project** artifact governs one project.

A runtime applies them side by side, and neither includes the other. They usually go in
different places. The Domain artifact goes at the broadest level that covers all of that
owner's work and nothing else. The Project artifact goes at the level that covers only that
project. If you work in several Domains, such as a client organization and your own work, place
each Domain artifact where it covers only that Domain's work.

## Keep the identity in any rendering

Some services read only Markdown or plain text in a settings field. In those cases you may
render the artifact rather than place the YAML as-is. Whatever form you use, we recommend keeping
these:

- the bundle `id`, `type`, and `version`;
- the `source_digest`;
- the self-identification rule (`<bundle-name>/identity`), as the first rule;
- each rule and fact `id`.

With these, you or an auditor can match a rendering to the exact versioned content it came from.
You can also ask the agent which governance bundles are active. A short header at the top of a
rendering is enough:

```markdown
<!-- SCS runtime artifact: bundle:medtech-cdmo, type domain, version 1.0.0,
     source_digest sha256:8c49...a840. Rendered from dist/medtech-cdmo-1.0.0.yaml. -->
```

Where a service accepts a Markdown file, the least lossy rendering is often the YAML itself
inside a fenced code block, below a one-line heading. That changes nothing in the content.

A `DRAFT` artifact has no `source_digest` and its version is `DRAFT+<digest>`. It is meant for
trying things out, not for placing where other people rely on it.

## Pages

| Service | Page | Checked |
|---|---|---|
| Claude Enterprise (claude.ai) | [claude-enterprise.md](claude-enterprise.md) | 2026-10-28 |
| Claude Code | [claude-code.md](claude-code.md) | 2026-10-28 |
| Cursor | [cursor.md](cursor.md) | 2026-10-28 |
| GitHub Copilot | [github-copilot.md](github-copilot.md) | 2026-10-28 |
| ChatGPT Enterprise | [chatgpt-enterprise.md](chatgpt-enterprise.md) | 2026-10-28 |

## Notes common to every service

- Each service treats instruction files as context, not as enforcement. None of the docs
  checked here promise the model will follow every instruction. Several warn that conflicting
  instructions may be followed unpredictably. Keep Domain and Project rules consistent.
  RFC 0002's layer-conflict review exists for this reason.
- Size limits differ widely. Some fields hold only a few thousand characters, which is less than
  a small Domain artifact. For example, `examples/two-tier-governance/compiled/global.yaml` is
  about 3,300 bytes. Each page gives the limits it could confirm.
- Whether a service loads both layers in a given session is the service's behaviour. SCS does
  not test it. Each page describes what the vendor documents.

## Previewing a stack

Once you know which artifacts a service loads together, and in what order, `scs stack` shows
what a session receives. Give the artifacts outermost first, in the order the page for your
service describes:

```bash
scs stack ~/jdoe-context/domain/dist/jdoe-1.0.0.yaml \
          dist/medtech-cdmo-1.2.0.yaml \
          projects/infusion-pump-fw/dist/infusion-pump-fw-1.0.0.yaml
```

It lists every rule and fact with the layer it came from, and reports a bundle in two layers,
a directive that mentions what another layer prohibits, identical text in two layers, and
`DRAFT` layers ([runtime-artifact.md](../../spec/0.7/runtime-artifact.md) §5). It reads only
and changes nothing. It checks the artifacts, not the service: a rendering placed in a settings
field is not read back.
