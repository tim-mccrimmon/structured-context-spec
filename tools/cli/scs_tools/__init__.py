"""
SCS Tools - CLI tools for Structured Context Specification project scaffolding
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

# Read from package metadata so the version can't drift from pyproject.toml (ISS-042).
try:
    __version__ = _pkg_version("scs-tools")
except PackageNotFoundError:
    __version__ = "unknown"
