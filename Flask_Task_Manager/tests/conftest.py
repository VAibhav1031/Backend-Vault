# tests/conftest.py
import pytest
from flask_task_manager import create_app, db


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


# User + Login fixture
@pytest.fixture
def token(client):
    client.post(
        "/api/auth/signup",
        json={
            "username": "Rangoo",
            "email": "Rangoo213@gmail.com",
            "password": "draco1234",
        },
    )
    payload = {"email": "Rangoo213@gmail.com", "password": "draco1234"}
    request = client.post("/api/auth/login", json=payload)
    assert request.status_code == 200
    return request.get_json()["token"]


@pytest.fixture
def auth_headers(token):
    """Normal API JWT headers"""
    return {"Authorization": f"Bearer {token}"}


# OTP + Reset flow fixtures
@pytest.fixture
def verify_token(client):
    client.post(
        "/api/auth/signup",
        json={
            "username": "Rangoo",
            "email": "vaibhavgrand2004@gmail.com",
            "password": "draco1234",
        },
    )
    request = client.post(
        "/api/auth/forget-password", json={"email": "vaibhavgrand2004@gmail.com"}
    )
    assert request.status_code == 200
    return {
        "otp-token": request.json["otp-token"],
        "otp": request.json["otp"],
    }


@pytest.fixture
def reset_headers(verify_token):
    """Headers for OTP verification step"""
    return {"Authorization": f"Bearer {verify_token['otp-token']}"}


@pytest.fixture
def verify_otp(client, verify_token, reset_headers):
    request = client.post(
        "/api/auth/verify-otp",
        json={"otp": verify_token["otp"], "email": "vaibhavgrand2004@gmail.com"},
        headers=reset_headers,
    )
    assert request.status_code == 200
    return request.json["reset-token"]
