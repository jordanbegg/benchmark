from fastapi.testclient import TestClient

from .fixtures import client_fixture, session_fixture


def test_create_muscle_group(client: TestClient):
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None


def test_read_muscle_group(client: TestClient):
    # sourcery skip: extract-duplicate-method
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.get(f"/musclegroups/{created_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] == created_id
    assert data["exercises"] == []


def test_read_muscle_groups(client: TestClient):
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.get("/musclegroups/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Chest"
    assert data[0]["id"] == created_id


def test_delete_muscle_group(client: TestClient):
    response = client.post("/musclegroups/", json={"name": "Chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.delete(f"/musclegroups/{created_id}")
    data = response.json()
    assert response.status_code == 200

    response = client.get(f"/musclegroups/{created_id}")
    data = response.json()
    assert response.status_code == 404


def test_update_muscle_group(client: TestClient):
    # sourcery skip: extract-duplicate-method
    response = client.post("/musclegroups/", json={"name": "chest"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "chest"
    assert data["id"] is not None

    created_id = data["id"]
    response = client.patch(
        f"/musclegroups/{created_id}", json={"name": "Chest"}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Chest"
    assert data["id"] == created_id
