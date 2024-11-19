from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture
from .utils import create_planned_set


def test_create_planned_set(client: TestClient):
    response = create_planned_set(client=client)
    data = response.json()

    assert response.status_code == 200
    assert data["reps"] == 5
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workoutroutine_id"] == 1


def test_read_planned_set(client: TestClient):
    response = create_planned_set(client=client)

    # Read the workout
    response = client.get("/planned_sets/2")
    data = response.json()
    assert response.status_code == 200
    assert data["reps"] == 5
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workoutroutine_id"] == 1


def test_read_planned_sets(client: TestClient):
    response = create_planned_set(client=client)

    response = client.get("/planned_sets/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data[1]["reps"] == 5
    assert data[1]["id"] is not None
    assert data[1]["exercise_id"] == 1
    assert data[1]["workoutroutine_id"] == 1


def test_delete_planned_set(client: TestClient):
    response = create_planned_set(client=client)

    response = client.delete("/planned_sets/1")
    assert response.status_code == 200

    # Check the set was deleted
    response = client.get("/planned_sets/1")
    assert response.status_code == 404


def test_update_planned_set(client: TestClient):
    response = create_planned_set(client=client)

    payload = {
        "reps": 100,
    }
    response = client.patch(
        "/planned_sets/1",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["reps"] == 100
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workoutroutine_id"] == 1
