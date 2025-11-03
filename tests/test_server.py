"""Tests for Flask server."""

import pytest
from vtexdocs_guardrails.server import create_app
from vtexdocs_guardrails.config import Config


@pytest.fixture
def app():
    """Create test app."""
    config = Config(
        jailbreak_threshold=0.5,
        jailbreak_device="cpu",
        environment="development"
    )
    app = create_app(config)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_endpoint(client):
    """Test /health returns correct status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['model_loaded'] is True
    assert data['validator'] == 'detect_jailbreak'


def test_validate_endpoint_safe_input(client):
    """Test /validate with safe input."""
    response = client.post('/validate', 
        json={"text": "How do I configure VTEX IO?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_safe'] is True
    assert 'score' in data
    assert 'latency_ms' in data


def test_validate_endpoint_missing_text(client):
    """Test /validate with missing text field."""
    response = client.post('/validate', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_validate_endpoint_invalid_threshold(client):
    """Test /validate with invalid threshold."""
    response = client.post('/validate',
        json={"text": "test", "threshold": 1.5})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_metrics_endpoint(client):
    """Test /metrics endpoint."""
    # Make some requests first
    client.post('/validate', json={"text": "test query"})
    
    response = client.get('/metrics')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_requests'] >= 1
    assert 'blocked_requests' in data
    assert 'avg_latency_ms' in data
