from flask import Blueprint, jsonify, request, abort
from flask_task_manager import db
from flask_task_manager.models import User, Task
from flask_task_manager import bcrypt
from utils import token_required, generate_token
from schemas import UserSchema, AddTask, ValidationError

main = Blueprint("main", __name__, url_prefix="/api/")


# now lets add the user auth something
# since it is backend service there is no need for the GET , json will do
@main.route("/signup", methods=["POST"])
def signup():
    schema = UserSchema()
    try:
        data = schema.loads(request.get_json())
    except ValidationError as err:
        return {"erros": err.messages}, 400

    hashed_password = bcrypt.generate_password_hash(
        data["password"]).decode("utf-8")
    user_name = data["username"]
    new_user = User(username=user_name, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"{user_name} user created Sucessfully"})


# this is the most important part because we are generatingt the token , which is necessary for the stateless feature


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


@main.route("/tasks", methods=["GET"])
@token_required
def get_tasks_all(user_id):
    tasks = Task.query.filter_by(
        user_id=user_id
    ).all()  # will get all the ask of the user

    if not tasks:
        return jsonify([])
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
        return jsonify({"error": "Task not found"}), 404
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
        data = schema.loads(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    if data.get("user_id"):
        # no user_id is required  while adding task , mostly JWT token will get that
        return jsonify({"error": "Not Authorized"}), 403

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
