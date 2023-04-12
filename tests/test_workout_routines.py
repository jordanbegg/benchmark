from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture


def test_create_empty_workout_routine(client: TestClient):
    # Create the workout routine
    payload = {"name": "Test Routine"}
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"] == []


def test_create_workout_routine(client: TestClient):
    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    # Create the workout routine
    exericse_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exericse_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exericse_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4


def test_read_workout_routine(client: TestClient):
    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    # Create the workout routine
    exericse_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exericse_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exericse_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Read the workout routine
    created_id = data["id"]
    response = client.get(f"/workout_routines/{created_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] == created_id
    assert data["exercises"][0]["id"] == exericse_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4


def test_read_workout_routines(client: TestClient):
    # Create the workout routine
    payload = {"name": "Test Routine"}
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"] == []

    created_id = data["id"]
    response = client.get("/workout_routines/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Test Routine"
    assert data[0]["id"] == created_id


def test_delete_workout_routine(client: TestClient):
    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    # Create the workout routine
    exericse_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exericse_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exericse_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    created_id = data["id"]
    response = client.delete(f"/workout_routines/{created_id}")
    data = response.json()
    assert response.status_code == 200

    # TODO Check the planned_sets were deleted

    # Check the routine was deleted
    response = client.get(f"/workout_routine/{created_id}")
    data = response.json()
    assert response.status_code == 404


def test_update_workout_routine(client: TestClient):
    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = client.post(
        "/exercises/",
        json={"name": "Bench Press"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"
    assert data["id"] is not None

    exercise_id = data["id"]

    # Create the workout routine
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 1}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["name"] == "Bench Press"
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 1

    workout_routine_id = data["id"]

    payload = {
        "name": "Test Routine 1",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 2}]}],
    }
    response = client.patch(
        f"/workout_routines/{workout_routine_id}",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine 1"
    assert data["id"] == workout_routine_id
    assert data["exercises"][0]["name"] == "Bench Press"
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 2
    assert len(data["exercises"][0]["planned_sets"]) == 1
