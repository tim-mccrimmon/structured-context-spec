# Examples

Two Domain repositories, built with the engine (`scs`) the way the skills build one, and two
reference ontologies.

| Example | What it shows |
|---|---|
| [`medtech-cdmo/`](medtech-cdmo/) | A fictional medical-device CDMO: a Domain on the `cdmo` ontology and one Project (`infusion-pump-fw`), each released as 1.0.0 and compiled |
| [`personal/`](personal/) | A fictional independent consultant: a Domain on the `personal` ontology, with the boundaries it supplies and two concepts defined with the owner |
| [`medical-device-cdmo/`](medical-device-cdmo/) | The reference ontology behind `scs new domain --ontology cdmo` |
| [`merchant-cash-advance/`](merchant-cash-advance/) | The reference ontology behind `--ontology mca` |

## How the Domain repositories are made

Each Domain example is a `recipe.yaml` and the repository it produces, checked in without its
`.git` directory. `build.py` runs the recipe through the engine:

1. `scs new domain`, then `scs new project` for each Project
2. `scs add bundle --new` for each concept the recipe defines
3. `scs bundle remove-scd` for every template SCD the checked-in repository does not have
4. `scs scd write` for each SCD it does have
5. `scs intake set` for the recipe's intake fields (owners, approvers, and so on)
6. `scs commit`, `scs bundle release`, `scs compile --version`, and a commit of `dist/`

The clock and the git dates are fixed to the recipe's `date` (`SOURCE_DATE_EPOCH`), so a
rebuild produces the same bytes. CI runs `python examples/build.py --check` and fails if the
checked-in files differ from a rebuild.

```bash
pip install -e tools/scd-validator -e tools/cli
python examples/build.py --check            # are the examples current?
python examples/build.py                    # rebuild them after an engine or content change
python examples/build.py --keep /tmp/ex     # also keep each repository with its git history
cd /tmp/ex/medtech-context && git tag       # domain/medtech-v1.0.0, ...
scs compile domain/bundles/domain-bundle.yaml --version 1.0.0 --stdout
```

To change an example, edit its SCDs under `context/project/` or its `recipe.yaml`, then run
`python examples/build.py`.

People, companies, and addresses in the examples are fictional; addresses use the reserved
`.test` domain.
