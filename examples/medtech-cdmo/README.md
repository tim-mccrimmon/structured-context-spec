# MedTech CDMO

A fictional contract developer and manufacturer of medical devices. `medtech-context/` is its
Domain repository, built by [`../build.py`](../build.py) from [`recipe.yaml`](recipe.yaml).

| Workspace | Bundle | SCDs | Compiled |
|---|---|---|---|
| `domain/` | `bundle:medtech` 1.0.0 | 7, in 6 concepts | [`domain/dist/medtech-1.0.0.yaml`](medtech-context/domain/dist/medtech-1.0.0.yaml) |
| `projects/infusion-pump-fw/` | `bundle:infusion-pump-fw` 1.0.0 | 2, in 2 concepts | [`projects/infusion-pump-fw/dist/infusion-pump-fw-1.0.0.yaml`](medtech-context/projects/infusion-pump-fw/dist/infusion-pump-fw-1.0.0.yaml) |

What to look at:

- `domain/context/project/`: the SCDs. Prohibitions (`prohibited.yaml`) compile first, as
  `Prohibited: <subject>.`; directives become rules; facts compile into a separate list.
- `domain/bundles/concepts/`: one bundle per concept, each with an `owner` role. The
  `cdmo` templates that did not apply (supplier qualification, training, security, and more)
  were retired.
- `domain/intake.yaml`: who owns each role, and who approves versions.
- `domain/bundles/medtech-v1.0.0.yaml` and `-MANIFEST.yaml`: the released snapshot and its
  manifest, with the approver and the content digest. The compiled artifact carries the same
  digest as `source_digest`.
- The Project inherits the Domain's rules at runtime. The two are compiled separately and
  neither imports the other.
