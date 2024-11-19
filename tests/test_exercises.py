from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture
from .utils import create_muscle_group, create_exercise


def test_create_exercise(client: TestClient):
    response = create_exercise(client=client)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "bench press"
    assert data["id"] is not None
    assert data["musclegroups"][0]["name"] == "chest"


def test_read_exercise(client: TestClient):
    # sourcery skip: extract-duplicate-method
    # Create the exercise
    response = create_exercise(client=client)

    # Read the exercise
    response = client.get("/exercises/1")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "bench press"
    assert data["id"] == 1
    assert data["musclegroups"][0]["name"] == "chest"


def test_read_exercises(client: TestClient):
    # Create the exercise
    response = create_exercise(client=client)
    data = response.json()

    response = client.get("/exercises/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "bench press"
    assert data[0]["id"] == 1


def test_delete_exercise(client: TestClient):
    # Create the exercise
    response = create_exercise(client=client)

    response = client.delete("/exercises/1")
    assert response.status_code == 200

    response = client.get("/exercises/1")
    assert response.status_code == 404


def test_update_exercise(client: TestClient):
    # Create the exercise
    response = create_exercise(client=client)
    data = response.json()

    # Create a muscle group
    response = create_muscle_group(client=client, payload={"name": "triceps"})

    response = client.patch(
        "/exercises/1",
        json={"name": "bench press", "musclegroup_ids": [1, 2]},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "bench press"
    assert data["id"] == 1
    assert data["musclegroups"][1]["name"] == "triceps"
