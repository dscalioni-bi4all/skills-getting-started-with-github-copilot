import copy
import pytest

from fastapi.testclient import TestClient

from src.app import app, activities


initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Restore the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity checks
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Basketball Team"
    email = "test.student@mergington.edu"

    # Ensure starting state has no participants for this activity
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Now the participant should be present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Confirm removal
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
