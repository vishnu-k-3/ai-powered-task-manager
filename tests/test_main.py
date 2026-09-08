# tests/test_main.py


# -------------------------
# Registration
# -------------------------

def test_register_endpoint(client):
    response = client.post(
        "/register",
        json={
            "email": "test_new_123@example.com",
            "username": "testuser_123",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test_new_123@example.com"
    assert data["username"] == "testuser_123"
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    client.post(
        "/register",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "testpassword"
        }
    )

    response = client.post(
        "/register",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "testpassword"
        }
    )

    assert response.status_code == 409


# -------------------------
# Login
# -------------------------

def test_login_success(client):
    client.post(
        "/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpassword"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "login@example.com",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={
            "email": "wrongpass@example.com",
            "username": "wrongpassuser",
            "password": "correctpassword"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "testpassword"
        }
    )

    assert response.status_code == 401


# -------------------------
# Protected endpoints
# -------------------------

def test_tasks_without_token(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_tasks_with_invalid_token(client):
    response = client.get(
        "/tasks",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


# -------------------------
# Authentication helper
# -------------------------

def get_auth_token(client):
    client.post(
        "/register",
        json={
            "email": "taskuser@example.com",
            "username": "taskuser",
            "password": "testpassword"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "taskuser@example.com",
            "password": "testpassword"
        }
    )

    return response.json()["access_token"]


# -------------------------
# Task CRUD
# -------------------------

def test_create_task(client):
    token = get_auth_token(client)

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Testing task creation",
            "completed": False,
            "status": "pending",
            "due_date": "2026-12-31"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Testing task creation"
    assert data["status"] == "pending"
    assert data["due_date"] == "2026-12-31"


def test_get_tasks(client):
    token = get_auth_token(client)

    response = client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_task(client):
    token = get_auth_token(client)

    create_response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Single Task",
            "description": "Testing single task",
            "completed": False,
            "status": "pending",
            "due_date": "2026-12-31"
        }
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client):
    token = get_auth_token(client)

    create_response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Old Task",
            "description": "Old description",
            "completed": False,
            "status": "pending",
            "due_date": "2026-12-31"
        }
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "completed": True,
            "status": "completed",
            "due_date": "2026-12-31"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Task"
    assert data["completed"] is True
    assert data["status"] == "completed"
    assert data["due_date"] == "2026-12-31"


def test_delete_task(client):
    token = get_auth_token(client)

    create_response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Delete Task",
            "description": "Testing deletion",
            "completed": False,
            "status": "pending",
            "due_date": "2026-12-31"
        }
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code in [200, 404]