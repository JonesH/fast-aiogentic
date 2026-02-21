"""Smoke test to verify project setup."""
from http import HTTPStatus

import fast_aiogentic

from fastapi.testclient import TestClient

from fast_aiogentic.api.main import app

client = TestClient(app)



def test_smoke():
    """Basic smoke test to ensure testing works."""
    assert True


def test_import():
    """Test that the package can be imported."""
    assert fast_aiogentic.__version__



def test_root_endpoint():
    """Test root endpoint returns status ok."""
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "ok"


def test_health_endpoint():
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "healthy"
