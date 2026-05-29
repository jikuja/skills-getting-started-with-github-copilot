import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity_name in payload
    assert "description" in payload[expected_activity_name]
    assert "participants" in payload[expected_activity_name]
    assert isinstance(payload[expected_activity_name]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "duplicate@mergington.edu"

    # Act
    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_deletes_existing_participant(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    assert email in activities["Chess Club"]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participant?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participant?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
