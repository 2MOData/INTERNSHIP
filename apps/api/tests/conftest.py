import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import agent_repository


@pytest.fixture(autouse=True)
def clear_agent_repository() -> None:
    agent_repository.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)