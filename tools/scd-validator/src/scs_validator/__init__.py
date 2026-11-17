"""SCS Validator - Validation tool for Structured Context Specification documents."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

# Read from package metadata so the version can't drift from pyproject.toml (ISS-042).
try:
    __version__ = _pkg_version("scs-validator")
except PackageNotFoundError:
    __version__ = "unknown"
__author__ = "Timothy McCrimmon"
