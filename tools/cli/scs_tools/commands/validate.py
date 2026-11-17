"""
Validate command - `scs validate` is the scs-validator command, registered under the `scs` group.

The command object is imported from scs-validator rather than re-declared here, so its options
(--bundle, --domain, --checkpoint, --strict, --json, --schema-dir, ...) always match
`scs-validate` and cannot drift out of sync with it.
"""

from scs_validator.commands.validate import validate

__all__ = ["validate"]
