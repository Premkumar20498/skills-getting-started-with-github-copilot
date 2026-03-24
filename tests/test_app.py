import pytest
from fastapi.testclient import TestClient
import importlib
import src.app


@pytest.fixture
def client():
    # Reset the module to clear in-memory state between tests
    importlib.reload(src.app)
    return TestClient(src.app.app)


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    # Check structure
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up test@example.com for Chess Club" == result["message"]
    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]


def test_signup_duplicate(client):
    client.post("/activities/Chess%20Club/signup?email=test@example.com")
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 409
    result = response.json()
    assert "Student already registered" == result["detail"]


def test_signup_missing_activity(client):
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" == result["detail"]


def test_delete_participant(client):
    client.post("/activities/Chess%20Club/signup?email=test@example.com")
    response = client.delete("/activities/Chess%20Club/participants?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Removed test@example.com from Chess Club" == result["message"]
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" not in data["Chess Club"]["participants"]


def test_delete_missing_activity(client):
    response = client.delete("/activities/Nonexistent/participants?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" == result["detail"]


def test_delete_missing_participant(client):
    response = client.delete("/activities/Chess%20Club/participants?email=nonexistent@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Participant not found" == result["detail"]