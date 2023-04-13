from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture


def test_create_workout(client: TestClient):
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

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 4, "weight": 60}]}
        ],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == workout_routine_id


def test_create_workout_with_bad_exercise(client: TestClient):
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

    # Create an exercise
    # sourcery skip: extract-duplicate-method
    response = client.post(
        "/exercises/",
        json={"name": "Triceps"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Triceps"
    assert data["id"] is not None

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [{"id": 1, "sets": [{"reps": 4, "weight": 60}]}],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 404


def test_read_workout(client: TestClient):
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

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 4, "weight": 60}]}
        ],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == workout_routine_id

    # Read the workout
    created_id = data["id"]
    response = client.get(f"/workouts/{created_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] == created_id
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60


def test_read_workouts(client: TestClient):
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

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 4, "weight": 60}]}
        ],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == workout_routine_id

    created_id = data["id"]
    response = client.get("/workouts/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["date"] == "1990-01-01"
    assert data[0]["id"] == created_id


def test_delete_workout(client: TestClient):
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

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 4, "weight": 60}]}
        ],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == workout_routine_id

    created_id = data["id"]
    response = client.delete(f"/workouts/{created_id}")
    data = response.json()
    assert response.status_code == 200

    # TODO Check the sets were deleted

    # Check the workout was deleted
    response = client.get(f"/workouts/{created_id}")
    data = response.json()
    assert response.status_code == 404


def test_update_workout(client: TestClient):
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

    # Create a workout routine
    exercise_id = data["id"]
    payload = {
        "name": "Test Routine",
        "exercises": [{"id": exercise_id, "planned_sets": [{"reps": 4}]}],
    }
    response = client.post(
        "/workout_routines/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Routine"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["planned_sets"][0]["reps"] == 4

    # Create a workout
    workout_routine_id = data["id"]
    payload = {
        "date": "1990-01-01",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 4, "weight": 60}]}
        ],
        "workoutroutine_id": workout_routine_id,
    }
    response = client.post(
        "/workouts/",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-01"
    assert data["id"] is not None
    assert data["exercises"][0]["id"] == exercise_id
    assert data["exercises"][0]["sets"][0]["weight"] == 60
    assert data["workoutroutine_id"] == workout_routine_id

    workout_id = data["id"]

    payload = {
        "date": "1990-01-02",
        "exercises": [
            {"id": exercise_id, "sets": [{"reps": 2, "weight": 1000}]}
        ],
    }
    response = client.patch(
        f"/workouts/{workout_id}",
        json=payload,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == "1990-01-02"
    assert data["id"] == workout_id
    assert data["exercises"][0]["name"] == "Bench Press"
    assert data["exercises"][0]["sets"][0]["reps"] == 2
    assert data["exercises"][0]["sets"][0]["weight"] == 1000
    assert len(data["exercises"][0]["sets"]) == 1
