import os
import pytest
from fastapi.testclient import TestClient 

os.environ.setdefault("AUTO_INGEST_ON_STARTUP", "false")

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)