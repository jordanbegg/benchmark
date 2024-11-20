from fastapi.testclient import TestClient

from .utils import create_workout_routine


def test_create_empty_workout_routine(client: TestClient):
    # Create the workout routine
    payload = {"name": "test routine"}
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test routine"
    assert data["id"] is not None
    assert data["exercises"] == []


def test_create_workout_routine(client: TestClient):
    response = create_workout_routine(client=client)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == 1
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4


def test_read_workout_routine(client: TestClient):
    # Create the workout routine
    response = create_workout_routine(client=client)

    # Read the workout routine
    response = client.get("/workout_routines/1")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test routine"
    assert data["id"] == 1
    assert data["exercises"][0]["id"] == 1
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4


def test_read_workout_routines(client: TestClient):
    response = create_workout_routine(client=client)

    response = client.get("/workout_routines/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "test routine"
    assert data[0]["id"] == 1


def test_delete_workout_routine(client: TestClient):
    response = create_workout_routine(client=client)

    response = client.delete("/workout_routines/1")
    assert response.status_code == 200

    # TODO Check the planned_sets were deleted

    # Check the routine was deleted
    response = client.get("/workout_routines/1")
    assert response.status_code == 404


def test_update_workout_routine(client: TestClient):
    # sourcery skip: extract-duplicate-method
    # Create an exercise
    response = create_workout_routine(client=client)
    data = response.json()

    payload = {
        "name": "test routine 1",
        "exercises": [{"id": 1, "planned_sets": [{"reps": 2}]}],
    }
    response = client.patch(
        "/workout_routines/1",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test routine 1"
    assert data["id"] == 1
    assert data["exercises"][0]["name"] == "bench press"
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 2
    assert len(data["exercises"][0]["planned_sets"]) == 1
