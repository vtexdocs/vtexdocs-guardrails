"""VTEX Docs Guardrails - Jailbreak detection service."""

__version__ = "0.1.0"

from .validator import JailbreakValidator
from .server import create_app

__all__ = ["JailbreakValidator", "create_app"]
