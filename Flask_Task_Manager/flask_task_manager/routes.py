from flask import Blueprint, jsonify, request, abort, current_app
from flask_task_manager import db
from flask_task_manager.models import User, Task
from flask_task_manager import bcrypt
from functools import wraps
import datetime
import jwt


main = Blueprint("main", __name__)


# now lets add the user auth something
# since it is backend service there is no need for the GET , json will do
@main.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data["password_hash"]).decode(
        "utf-8"
    )
    user_name = data["username"]
    new_user = User(username=user_name, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"{user_name} user created Sucessfully"})


# this is the most important part because we are generatingt the token , which is necessary for the stateless feature


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
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
        return None  # token_expired
    except jwt.InvalidTokenError:
        return None  # invalid


@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_name = data["username"]
    # /one()  we can use that since there will only user with that username
    user = User.query.filter_by(username=user_name).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid username or password"}), 401

    token = generate_token(user.id)
    # here we have to give the jwt token for future
    return jsonify({"token": token})


# Authorization: Bearer <your_jwt_here> the  payload must be this  when it is sent  by the client


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing "}), 401

        token = auth_header.split(" ")[1]
        user_id = decode_token(token)
        if not user_id:
            return jsonify({"error": "Token is invalid"}), 401

        return func(user_id, *args, **kwargs)

    return wrapper


@main.route("/tasks<int:id>", methods=["GET"])
@token_required
def get_tasks(user_id, id):
    task = Task.query.filter_by(id=id).first()

    return jsonify(
        [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completion": task.completion,
                "user_id": task.user_id,
            }
        ]
    )


@main.route("/tasks", methods=["POST"])
@token_required
def add_task(user_id):
    data = request.get_json()
    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        user_id=user_id,
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added", "task_id": new_task.id}), 201


@main.route("/tasks/<int:id>", methods=["DELETE"])
@token_required
def delete(user_id, id):
    # this will get me the object of the Tasks
    task = db.session.get(Task, id) or abort(404)
    # now i have to delete the  particular associated with the id
    if task.user_id != user_id:
        return jsonify({"error": "Not Authorized"}), 403
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task {id} deleted"})
