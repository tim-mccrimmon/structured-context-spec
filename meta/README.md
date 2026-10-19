# SCS Meta Bundle

The meta bundle published with SCS 0.6.0: `bundle:meta`, version `0.6.0`.

It is maintained by the SCS specification and is read-only to adopters. A Domain bundle pins
it in its imports:

```yaml
imports:
  - bundle:meta:0.6.0
```

Adopters do not copy it into their repositories. The validator and `scs compile` ship with
this bundle and resolve `bundle:meta` to it, so a pinned import resolves wherever the tools
are installed. (A copy is vendored into `tools/scd-validator/src/scs_validator/meta/` by
`tools/scd-validator/scripts/sync_schemas.py`.)

Contents:

- `scd:meta:governance-context` — the terms SCS governance context uses (Domain bundle,
  Project bundle, rule, citation) and three directives that tell an agent how to read it.
  The directives compile into every Domain bundle's runtime artifact.
