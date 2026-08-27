from fastapi.testclient import TestClient
import json
import pytest
from app.main import app
import app.storage as storage

client = TestClient(app)

@pytest.fixture
def task_file(tmp_path, monkeypatch):
    file_path = tmp_path / "tasks.json"

    file_path.write_text("[]")

    monkeypatch.setattr(storage, "TASKS_FILE", file_path)

    return file_path

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_tasks(task_file):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []

def test_create_task(task_file):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "description": "Write automated tests"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Learn pytest"
    assert data["description"] == "Write automated tests"
    assert data["completed"] is False

    contents = json.loads(task_file.read_text())

    assert len(contents) == 1
    assert contents[0]["title"] == "Learn pytest"

def test_get_task(task_file):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Learn CI/CD",
            "description": "Build a pipeline"
        }
    )

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Learn CI/CD"

def test_get_missing_task(task_file):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_update_task(task_file):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Old title",
            "description": "Old description"
        }
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "New title",
            "description": "New description",
            "completed": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "New title"
    assert data["description"] == "New description"
    assert data["completed"] is True

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.json()["title"] == "New title"
    assert get_response.json()["completed"] is True

def test_update_missing_task(task_file):
    response = client.put(
        "/tasks/999",
        json={
            "title": "Doesn't exist",
            "description": "No task",
            "completed": False
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}

def test_delete_task(task_file):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete me",
            "description": "Testing DELETE"
        }
    )

    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404

def test_delete_missing_task(task_file):
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}

def test_create_task_requires_title(task_file):
    response = client.post(
        "/tasks",
        json={
            "description": "No title"
        }
    )

    assert response.status_code == 422

def test_task_ids_are_not_reused(task_file):
    first = client.post(
        "/tasks",
        json={
            "title": "First",
            "description": ""
        }
    )

    second = client.post(
        "/tasks",
        json={
            "title": "Second",
            "description": ""
        }
    )

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    client.delete(f"/tasks/{first_id}")

    third = client.post(
        "/tasks",
        json={
            "title": "Third",
            "description": ""
        }
    )

    third_id = third.json()["id"]

    assert first_id == 1
    assert second_id == 2
    assert third_id == 3

def test_update_persists(task_file):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original",
            "description": "Original description"
        }
    )

    task_id = create_response.json()["id"]

    client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated",
            "description": "Updated description",
            "completed": True
        }
    )

    contents = json.loads(task_file.read_text())

    assert contents[0]["title"] == "Updated"
    assert contents[0]["description"] == "Updated description"
    assert contents[0]["completed"] is True

def test_update_task_requires_all_fields(task_file):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test",
            "description": "Test"
        }
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated"
        }
    )

    assert response.status_code == 422

def test_create_multiple_tasks(task_file):
    first = client.post(
        "/tasks",
        json={
            "title": "First",
            "description": ""
        }
    )

    second = client.post(
        "/tasks",
        json={
            "title": "Second",
            "description": ""
        }
    )

    response = client.get("/tasks")

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["id"] == first.json()["id"]
    assert tasks[1]["id"] == second.json()["id"]

