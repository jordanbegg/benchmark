from fastapi.testclient import TestClient

MUSCLE_GROUP_PAYLOAD = {"name": "chest"}
EXERCISE_PAYLOAD = {"name": "bench press", "musclegroup_ids": [1]}
WORKOUT_ROUTINE_PAYLOAD = {
    "name": "test routine",
    "exercises": [{"id": 1, "planned_sets": [{"reps": 4}]}],
}
WORKOUT_PAYLOAD = {
    "date": "1990-01-01",
    "exercises": [{"id": 1, "sets": [{"reps": 4, "weight": 60}]}],
    "workoutroutine_id": 1,
}

SET_PAYLOAD = {
    "weight": 50,
    "reps": 5,
    "exercise_id": 1,
    "workout_id": 1,
}


def create_muscle_group(
    client: TestClient, payload: dict = MUSCLE_GROUP_PAYLOAD
):
    return client.post("/musclegroups/", json=payload)


def create_exercise(client: TestClient, payload: dict = EXERCISE_PAYLOAD):
    _ = create_muscle_group(client=client, payload=MUSCLE_GROUP_PAYLOAD)
    return client.post(
        "/exercises/",
        json=payload,
    )


def create_workout_routine(
    client: TestClient, payload: dict = WORKOUT_ROUTINE_PAYLOAD
):
    _ = create_exercise(client=client, payload=EXERCISE_PAYLOAD)
    return client.post(
        "/workout_routines/",
        json=payload,
    )


def create_workout(client: TestClient, payload: dict = WORKOUT_PAYLOAD):
    _ = create_workout_routine(client=client, payload=WORKOUT_ROUTINE_PAYLOAD)
    return client.post(
        "/workouts/",
        json=payload,
    )


def create_set(client: TestClient, payload: dict = SET_PAYLOAD):
    _ = create_workout(client=client, payload=WORKOUT_PAYLOAD)
    return client.post(
        "/sets/",
        json=payload,
    )
