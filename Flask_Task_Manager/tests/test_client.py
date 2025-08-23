# here i have one thing
import pytest
from flask_task_manager import create_app, db
from flask_task_manager.models import Task


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# now  we have to go and think for the  signup and login  letss goo
# Try to unauthorized access to another user Task


@pytest.fixture
def token(client):
    client.post(
        "/api/signup",
        json={
            "username": "Rangoo",
            "email": "Rangoo213@gmail.com",
            "password": "draco1234",
        },
    )
    # payload = {"username": "Rangoo", "password": "draco1234"}
    payload = {"email": "Rangoo213@gmail.com", "password": "draco1234"}
    # currently we are usingt he email as the login
    request = client.post("/api/auth/login", json=payload)
    assert request.status_code == 200
    data = request.get_json()
    assert "token" in data
    return data["token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_all(client, auth_headers):
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data["errors"]["status"] == 404
    assert data["errors"]["message"] == "Resource not found"


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
    payload = {"title": "New Test", "description": "For delete test ", "user_id": 5}

    response = client.post("/api/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "user_id" in response.json["errors"]["details"]

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
