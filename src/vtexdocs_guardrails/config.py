"""Configuration management for guardrails service."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Service configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8082
    debug: bool = False
    jailbreak_threshold: float = 0.5
    jailbreak_device: str = "cpu"
    environment: str = "production"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("GUARDRAILS_HOST", "0.0.0.0"),
            port=int(os.getenv("GUARDRAILS_PORT", "8082")),
            debug=os.getenv("ENVIRONMENT", "production") == "development",
            jailbreak_threshold=float(os.getenv("JAILBREAK_THRESHOLD", "0.5")),
            jailbreak_device=os.getenv("JAILBREAK_DEVICE", "cpu"),
            environment=os.getenv("ENVIRONMENT", "production"),
        )
