from fastapi.testclient import TestClient

from .utils import create_muscle_group


def test_create_muscle_group(client: TestClient):
    response = create_muscle_group(client=client)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "chest"
    assert data["id"] is not None


def test_read_muscle_group(client: TestClient):
    # sourcery skip: extract-duplicate-method
    response = create_muscle_group(client=client)
    data = response.json()

    response = client.get("/musclegroups/1")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "chest"
    assert data["id"] == 1
    assert data["exercises"] == []


def test_read_muscle_groups(client: TestClient):
    response = create_muscle_group(client=client)
    data = response.json()

    response = client.get("/musclegroups/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "chest"
    assert data[0]["id"] == 1


def test_delete_muscle_group(client: TestClient):
    response = create_muscle_group(client=client)
    _ = response.json()

    response = client.delete("/musclegroups/1")
    _ = response.json()
    assert response.status_code == 200

    response = client.get("/musclegroups/1")
    _ = response.json()
    assert response.status_code == 404


def test_update_muscle_group(client: TestClient):
    # sourcery skip: extract-duplicate-method
    response = create_muscle_group(client=client)
    data = response.json()

    response = client.patch("/musclegroups/1", json={"name": "triceps"})
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "triceps"
    assert data["id"] == 1
