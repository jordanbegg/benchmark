from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture
from .utils import create_workout, create_workout_routine, create_exercise


def test_create_workout(client: TestClient):
    response = create_workout(client=client)
    data = response.json()

    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == 1
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == 1


def test_create_workout_with_bad_exercise(client: TestClient):
    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = create_workout_routine(client=client)
    response = client.post("/exercises/", json={"name": "bad"})

    response = client.post(
        "/workouts/",
        json={
            "date": "1990-01-01",
            "exercises": [{"id": 2, "sets": [{"reps": 4, "weight": 60}]}],
            "workoutroutine_id": 1,
        },
    )
    assert response.status_code == 404


def test_read_workout(client: TestClient):
    response = create_workout(client=client)

    # Read the workout
    response = client.get("/workouts/1")
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] == 1
    assert data["exercises"][0]["id"] == 1
    assert data["exercises"][0]["sets"][0]["weight"] == 60


def test_read_workouts(client: TestClient):
    response = create_workout(client=client)

    response = client.get("/workouts/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["date"] == "1990-01-01"
    assert data[0]["id"] == 1


def test_delete_workout(client: TestClient):
    response = create_workout(client=client)

    response = client.delete("/workouts/1")
    assert response.status_code == 200

    # TODO Check the sets were deleted

    # Check the workout was deleted
    response = client.get("/workouts/1")
    assert response.status_code == 404


def test_update_workout(client: TestClient):
    response = create_workout(client=client)

    payload = {
        "date": "1990-01-02",
        "exercises": [{"id": 1, "sets": [{"reps": 2, "weight": 1000}]}],
    }
    response = client.patch(
        "/workouts/1",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-02"
    assert data["id"] == 1
    assert data["exercises"][0]["name"] == "Bench Press"
    assert data["exercises"][0]["sets"][0]["reps"] == 2
    assert data["exercises"][0]["sets"][0]["weight"] == 1000
    assert len(data["exercises"][0]["sets"]) == 1
