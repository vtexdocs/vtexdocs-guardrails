"""Tests for jailbreak validator."""

import pytest
from vtexdocs_guardrails.validator import JailbreakValidator


@pytest.fixture
def validator():
    """Create validator instance."""
    return JailbreakValidator(threshold=0.5, device="cpu")


def test_validator_initialization(validator):
    """Test validator initializes correctly."""
    assert validator.is_loaded is True
    assert validator.threshold == 0.5
    assert validator.device == "cpu"


def test_safe_input_passes(validator):
    """Test legitimate queries pass validation."""
    is_safe, score, reason = validator.validate("How do I configure VTEX IO?")
    assert is_safe is True
    assert score < 0.5
    assert reason is None


def test_empty_input(validator):
    """Test empty input is safe."""
    is_safe, score, reason = validator.validate("")
    assert is_safe is True
    assert score == 0.0
    assert reason is None


def test_threshold_configuration():
    """Test threshold can be configured."""
    validator_strict = JailbreakValidator(threshold=0.3, device="cpu")
    assert validator_strict.threshold == 0.3
    
    validator_lenient = JailbreakValidator(threshold=0.7, device="cpu")
    assert validator_lenient.threshold == 0.7
