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

def get_auth_token(client, email="taskuser@example.com", username="taskuser"):
    client.post(
        "/register",
        json={
            "email": email,
            "username": username,
            "password": "testpassword"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": email,
            "password": "testpassword"
        }
    )

    return response.json()["access_token"]


# -------------------------
# Task CRUD
# -------------------------

def test_create_task(client):
    token = get_auth_token(client, "creator@example.com", "creator")

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
    token = get_auth_token(client, "getter@example.com", "getter")

    response = client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_task(client):
    token = get_auth_token(client, "singletask@example.com", "singletask")

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
    token = get_auth_token(client, "updater@example.com", "updater")

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
    token = get_auth_token(client, "deleter@example.com", "deleter")

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

    assert get_response.status_code == 404


# -------------------------
# New Tests: Partial Update (exclude_unset=True)
# -------------------------

def test_partial_update_preserves_other_fields(client):
    token = get_auth_token(client, "partial@example.com", "partial")

    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Keep My Description",
            "description": "Important details here",
            "completed": False,
            "status": "pending",
            "due_date": "2026-12-31"
        }
    )
    task_id = create_response.json()["id"]

    # Update ONLY the status
    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "completed"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify status updated, but title and description were NOT wiped out
    assert data["status"] == "completed"
    assert data["title"] == "Keep My Description"
    assert data["description"] == "Important details here"


# -------------------------
# New Tests: Multi-User Task Ownership & Isolation
# -------------------------

def test_user_cannot_access_another_users_task(client):
    user1_token = get_auth_token(client, "user_sec_1@example.com", "user_sec_1")
    user2_token = get_auth_token(client, "user_sec_2@example.com", "user_sec_2")

    # User 1 creates a private task
    create_res = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={
            "title": "User 1 Secret Task",
            "description": "Secret",
            "completed": False,
            "status": "pending"
        }
    )
    user1_task_id = create_res.json()["id"]

    # User 2 tries to GET User 1's task -> 404
    get_res = client.get(
        f"/tasks/{user1_task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert get_res.status_code == 404

    # User 2 tries to PATCH User 1's task -> 404
    patch_res = client.patch(
        f"/tasks/{user1_task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"title": "Hacked Title"}
    )
    assert patch_res.status_code == 404

    # User 2 tries to DELETE User 1's task -> 404
    del_res = client.delete(
        f"/tasks/{user1_task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert del_res.status_code == 404


def test_user_task_list_isolation(client):
    user_a_token = get_auth_token(client, "user_a@example.com", "user_a")
    user_b_token = get_auth_token(client, "user_b@example.com", "user_b")

    # User A creates 2 tasks
    for i in range(2):
        client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": f"Task A {i}", "description": "Desc", "completed": False, "status": "pending"}
        )

    # User B creates 1 task
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {user_b_token}"},
        json={"title": "Task B 1", "description": "Desc", "completed": False, "status": "pending"}
    )

    # User A views their tasks: should ONLY see 2
    res_a = client.get("/tasks", headers={"Authorization": f"Bearer {user_a_token}"})
    assert len(res_a.json()) == 2

    # User B views their tasks: should ONLY see 1
    res_b = client.get("/tasks", headers={"Authorization": f"Bearer {user_b_token}"})
    assert len(res_b.json()) == 1


def test_status_filter_isolation(client):
    alice_token = get_auth_token(client, "alice@example.com", "alice")
    bob_token = get_auth_token(client, "bob@example.com", "bob")

    # Both Alice and Bob create a "completed" task
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "Alice Done", "description": "d", "completed": True, "status": "completed"}
    )
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"title": "Bob Done", "description": "d", "completed": True, "status": "completed"}
    )

    # Alice should only see her completed task
    res = client.get("/tasks/status/completed", headers={"Authorization": f"Bearer {alice_token}"})
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Alice Done"