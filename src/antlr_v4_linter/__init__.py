"""ANTLR v4 Grammar Linter - Static analysis for .g4 files."""

from .core.linter import ANTLRLinter
from .core.models import LinterConfig, Severity
from .core.config import load_config

__version__ = "0.1.1"
__author__ = "ANTLR v4 Linter Team"

__all__ = [
    "ANTLRLinter",
    "LinterConfig", 
    "Severity",
    "load_config",
]