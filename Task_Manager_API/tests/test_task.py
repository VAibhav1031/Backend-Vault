from flask_task_manager.models import Task


def test_get_all(client, auth_headers):
    request = client.get("/api/tasks", headers=auth_headers)
    assert request.status_code == 404
    data = request.get_json()
    assert data["errors"]["status"] == 404
    assert data["errors"]["message"] == "No Task found"


def test_get_filter(client, auth_headers):
    payload = {
        "title": "new test",
        "description": "for getting the task...",
    }
    payload1 = {
        "title": "new test2",
        "description": "for getting the task..:::)))",
        "completion": True,
    }

    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    response = client.post("/api/tasks", json=payload1, headers=auth_headers)
    assert response.status_code == 201

    task = Task.query.filter_by(title="new test2").first()
    print(task.completion)

    request = client.get(
        "/api/tasks?completion=true&title=new%20test2", headers=auth_headers
    )
    assert request.status_code == 200
    assert request.json["data"][0]["title"] == "new test2"


def test_get(client, app, auth_headers):
    payload = {
        "title": "new test",
        "description": "for getting the task",
    }

    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    task_id = response.get_json()["task_id"]

    request = client.get(f"/api/tasks/{task_id}", headers=auth_headers)

    assert request.status_code == 200

    # we have to use the app_context to run all flask related object
    with app.app_context():
        assert Task.query.filter_by(id=task_id).first() is not None


# newly added
# test


def test_add(client, app, auth_headers):
    payload = {
        "title": "new test",
        "description": "for delete test ",
    }

    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    task_id = response.get_json()["task_id"]

    with app.app_context():
        assert Task.query.filter_by(id=task_id).first() is not None


#
# test and delete


def test_add_and_delete_task(client, app, auth_headers):
    payload = {"title": "New Test", "description": "For delete test "}

    response = client.post("/api/tasks", json=payload, headers=auth_headers)

    return
    task_id = response.get_json()["task_id"]

    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert f"Task {task_id} deleted" in delete_response.get_json()["message"]

    with app.app_context():
        assert Task.query.filter_by(id=task_id).first() is None


def test_access_protected_without_token(client):
    res = client.get("/api/tasks")
    assert res.status_code == 401
    assert res.json["errors"]["reason"] == "token is missing"


def test_acess_task_without_title(client, auth_headers):
    payload = {"description": "without title"}

    response = client.post("/api/tasks", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert "title" in response.json["errors"]["details"]
