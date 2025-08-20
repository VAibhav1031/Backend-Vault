from flask import Blueprint, jsonify, request, abort
from flask_task_manager import db
from flask_task_manager.models import User, Task
from flask_task_manager import bcrypt
from flask_task_manager.utils import token_required, generate_token
from .error_handler import (
    handle_marshmallow_error,
    not_found,
    user_already_exists,
    unauthorized_error,
    forbidden_access,
)
from flask_task_manager.schemas import (
    RegisterSchema,
    AddTask,
    LoginSchema,
    ValidationError,
)

main = Blueprint("main", __name__, url_prefix="/api/")


# now lets add the user auth something
# since it is backend service there is no need for the GET , json will do
@main.route("/signup", methods=["POST"])
def signup():
    schema = RegisterSchema()
    try:
        # it is already in the dict form then we use load not loads
        data = schema.load(request.get_json())
    except ValidationError as err:
        # return {"erros": err.messages}, 400
        return handle_marshmallow_error(err)

    hashed_password = bcrypt.generate_password_hash(
        data["password"]).decode("utf-8")
    user_name = data["username"]
    email = data["email"]
    new_user = User(username=user_name, email=email,
                    password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"{user_name} user created Sucessfully"})


# this is the most important part because we are generatingt the token , which is necessary for the stateless feature


@main.route("/login", methods=["POST"])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return handle_marshmallow_error(err)

    if data.get("email"):
        # /one()  we can use that since there will only user with that username
        user = User.query.filter_by(email=data["email"]).first()
    else:
        user = User.query.filter_by(username=data["username"]).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return unauthorized_error(msg="Invalid Credentials")

    token = generate_token(user.id)
    # here we have to give the jwt token for future
    return jsonify({"token": token})


@main.route("/tasks", methods=["GET"])
@token_required
def get_tasks_all(user_id):
    tasks = Task.query.filter_by(
        user_id=user_id
    ).all()  # will get all the ask of the user

    if not tasks:
        return not_found()
    return jsonify(
        [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completion": t.completion,
                "user_id": t.user_id,
            }
            for t in tasks
        ]
    )


@main.route("/tasks/<int:task_id>", methods=["GET"])
@token_required
def get_task(user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return not_found()
    return jsonify(
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completion": task.completion,
        }
    )


@main.route("/tasks", methods=["POST"])
@token_required
def add_task(user_id):
    schema = AddTask()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return handle_marshmallow_error(err)

    if data.get("user_id"):
        # no user_id is required  while adding task , mostly JWT token will get that
        return forbidden_access("Forbidden")

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
        return forbidden_access("Forbidden,Not authorized to access other")
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task {id} deleted"})
