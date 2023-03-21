import pytest

from api import app

@pytest.fixture
def test_api():
    return app.test_client()
