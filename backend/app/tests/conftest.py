import pytest
from starlette.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="module")
def client():
    # Use TestClient for API tests
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def mock_settings():
    settings.TEST_MODE = True
    settings.DATABASE_URL = "sqlite:///:memory:" # Use in-memory DB for unit tests if possible
    # Note: Logic in app/db/base.py might need adjustment to support switching engine on fly
    # or we just rely on mocking CRUD for API tests.
    yield settings
