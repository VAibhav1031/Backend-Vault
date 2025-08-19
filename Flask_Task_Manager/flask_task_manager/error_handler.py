from flask import jsonify, request
import uuid

central_registry = {
    "USER_ALREADY_EXISTS": "User already exists, Try different",
    "UNAUTHORIZED": "Unauthorized access",
    "INVALID_INPUT": "Invalid input data",
    "NOT_FOUND": "Resource not found",
    "INTERNAL_ERROR": "Internal server error",
}


def _make_instance():
    return f"{request.path}#{uuid.uuid4()}"


def handle_marshmallow_error(err):
    response = {
        "errors": {
            "type": "ValidationError",
            "status": 400,
            "message": central_registry["INVALID_INPUT"],
            "details": err.messages,
        }
    }
    return jsonify(response), 400


def user_already_exists(msg):
    return jsonify(
        {
            "errors": {
                "type": "User already exist",
                "status": 409,
                "message": msg if msg else central_registry["USER_ALREADY_EXISTS"],
                "instance": "A",
            }
        }
    ), 409


def unauthorized_Error(msg):
    return jsonify(
        {
            "errors": {
                "type": "Unauthorized",
                "status": 401,
                "message": msg if msg else central_registry["UNAUTHORIZED"],
                "instance": "a",
            }
        }
    ), 401  # it is good to send the code beside for error


def token_error(token_msg):
    # I know it is bit same as the unauthorized_Error but , in this we will give is the token is expired or invalid more clearer then privious
    return jsonify(
        {
            "errors": {
                "type": "token error",
                "status": 401,
                "message": token_msg,
                "instance": "a",
            }
        }
    ), 401
