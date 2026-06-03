"""Entry point for running scs_validator as a module."""

from .commands.validate import validate

if __name__ == "__main__":
    validate()
