"""
Validate command - `scs validate` is the scs-validator command, registered under the `scs` group.

The command object is imported from scs-validator rather than re-declared here, so its options
(--bundle, --domain, --checkpoint, --strict, --schema-dir, ...) always match `scs-validate` and
cannot drift out of sync with it.
"""

import sys

import click

try:
    from scs_validator.commands.validate import validate

    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

    @click.command(
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def validate(**_):
        """Validate SCS documents and bundles (requires scs-validator)."""
        click.echo(
            "Error: scs-validator is not installed.\n" "Install it with: pip install scs-validator",
            err=True,
        )
        sys.exit(1)
