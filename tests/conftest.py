import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "")

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
