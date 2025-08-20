import datetime
from functools import wraps
from flask import current_app, jsonify
import jwt
from flask import request
from .error_handler import unauthorized_error


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
    }
    secret_key = current_app.config["SECRET_KEY"]
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms="HS256"
        )
        return payload["user_id"]

    except jwt.ExpiredSignatureError:
        return "token expired"  # token_expired
    except jwt.InvalidTokenError:
        return "token invalid"  # invalid


# Authorization: Bearer <your_jwt_here> the  payload must be this  when it is sent  by the client


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return unauthorized_error(msg="token error", reason="token is missing")

        token = auth_header.split(" ")[1]
        user_id = decode_token(token)
        if not isinstance(user_id, int):
            return unauthorized_error(msg="token error", reason=user_id)
        return func(user_id, *args, **kwargs)

    return wrapper
