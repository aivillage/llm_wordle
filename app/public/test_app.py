from fastapi.testclient import TestClient


from .main import app

@pytest.fixture(scope="session")
def set_env_vars():
    client = TestClient(app)
    os.environ["PUBLIC_SETTINGS_FILE"] = "public_settings.dev.json"
    yield client
    # Optionally, remove variables after tests
    del os.environ["PUBLIC_SETTINGS_FILE"]


def test_index(set_env_vars):
    client = set_env_vars
    response = client.get("/")
    assert response.cookies.get("my_cookie") is not None