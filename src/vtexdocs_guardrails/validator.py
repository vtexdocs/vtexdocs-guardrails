"""Jailbreak detection validator using Guardrails Hub."""

from typing import Tuple, Optional
from guardrails import Guard
from guardrails.hub import DetectJailbreak
import time
import logging

logger = logging.getLogger(__name__)


class JailbreakValidator:
    """Wrapper for Guardrails Hub detect_jailbreak validator."""
    
    def __init__(self, threshold: float = 0.5, device: str = "cpu"):
        """
        Initialize jailbreak validator.
        
        Args:
            threshold: Detection threshold (0.0-1.0), higher = stricter
            device: Device to run on (cpu, cuda, metal)
        """
        self.threshold = threshold
        self.device = device
        self._model_loaded = False
        
        try:
            self._guard = Guard().use(
                DetectJailbreak,
                threshold=threshold,
                on_fail="exception",
                device=device,
            )
            self._model_loaded = True
            logger.info(
                f"Jailbreak validator initialized "
                f"(threshold={threshold}, device={device})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize validator: {e}")
            raise
    
    def validate(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Validate text for jailbreak attempts.
        
        Args:
            text: Input text to validate
            
        Returns:
            (is_safe, score, reason)
            - is_safe: True if safe, False if jailbreak detected
            - score: 0.0-1.0, higher = more likely jailbreak
            - reason: Error message if unsafe, None otherwise
        """
        if not text or not text.strip():
            return True, 0.0, None
        
        start_time = time.perf_counter()
        
        try:
            # Run validation through Guard
            result = self._guard.validate(text)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            # Extract score from validation metadata
            score = getattr(result, 'validation_score', 0.0)
            
            logger.info(
                f"Validation passed: '{text[:50]}...' "
                f"(score={score:.3f}, latency={elapsed_ms:.1f}ms)"
            )
            return True, score, None
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            # On validation failure, assume jailbreak detected
            score = 1.0
            reason = str(e)
            
            logger.warning(
                f"Validation failed: '{text[:50]}...' "
                f"(score={score:.3f}, latency={elapsed_ms:.1f}ms) - {reason}"
            )
            return False, score, reason
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model_loaded
