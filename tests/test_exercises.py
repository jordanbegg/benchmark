from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture


def test_create_exercise(client: TestClient):
    # Create a muscle group
    # sourcery skip: extract-duplicate-method
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    # Create an exercise
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press", "musclegroup_ids": [data["id"]]},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None
    assert data["musclegroups"][0]["name"] == "Chest"


def test_read_exercise(client: TestClient):
    # Create a muscle group
    # sourcery skip: extract-duplicate-method
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    # Create the exercise
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press", "musclegroup_ids": [data["id"]]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None
    assert data["musclegroups"][0]["name"] == "Chest"

    # Read the exercise
    created_id = data["id"]
    response = client.get(f"/exercises/{created_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] == created_id
    assert data["musclegroups"][0]["name"] == "Chest"


def test_read_exercises(client: TestClient):
    # Create the exercise
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.get("/exercises/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Bench Press"
    assert data[0]["id"] == created_id


def test_delete_exercise(client: TestClient):
    # Create the exercise
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.delete(f"/exercises/{created_id}")
    data = response.json()
    assert response.status_code == 200

    response = client.get(f"/exercises/{created_id}")
    data = response.json()
    assert response.status_code == 404


def test_update_exercise(client: TestClient):
    # Create the exercise
    response = client.post(
        "/exercises/",
        json={"name": "bench press"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "bench press"
    assert data["id"] is not None

    # Create a muscle group
    # sourcery skip: extract-duplicate-method
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.patch(
        f"/exercises/{created_id}",
        json={"name": "Bench Press", "musclegroup_ids": [1]},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] == created_id
    assert data["musclegroups"][0]["name"] == "Chest"
