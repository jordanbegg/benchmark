from fastapi.testclient import TestClient

from .utils import create_set


def test_create_set(client: TestClient):
    response = create_set(client=client)
    data = response.json()

    assert response.status_code == 200
    assert data["weight"] == 50
    assert data["reps"] == 5
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workout_id"] == 1


def test_read_set(client: TestClient):
    response = create_set(client=client)

    # Read the workout
    response = client.get("/sets/2")
    data = response.json()
    assert response.status_code == 200
    assert data["weight"] == 50
    assert data["reps"] == 5
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workout_id"] == 1


def test_read_sets(client: TestClient):
    response = create_set(client=client)

    response = client.get("/sets/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data[1]["weight"] == 50
    assert data[1]["reps"] == 5
    assert data[1]["id"] is not None
    assert data[1]["exercise_id"] == 1
    assert data[1]["workout_id"] == 1


def test_delete_set(client: TestClient):
    response = create_set(client=client)

    response = client.delete("/sets/1")
    assert response.status_code == 200

    # TODO Check the sets were deleted

    # Check the set was deleted
    response = client.get("/sets/1")
    assert response.status_code == 404


def test_update_set(client: TestClient):
    response = create_set(client=client)

    payload = {
        "weight": 2,
        "reps": 100,
    }
    response = client.patch(
        "/sets/2",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["weight"] == 2
    assert data["reps"] == 100
    assert data["id"] is not None
    assert data["exercise_id"] == 1
    assert data["workout_id"] == 1
