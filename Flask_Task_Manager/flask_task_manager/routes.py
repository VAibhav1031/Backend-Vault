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
    internal_server_error,
    forbidden_access,
)
from flask_task_manager.schemas import (
    RegisterSchema,
    AddTask,
    LoginSchema,
    ValidationError,
)
import logging

main = Blueprint("main", __name__, url_prefix="/api/")

logger = logging.getLogger(__name__)

# now lets add the user auth something
# since it is backend service there is no need for the GET , json will do


@main.route("/signup", methods=["POST"])
def signup():
    schema = RegisterSchema()
    try:
        # it is already in the dict form then we use load not loads
        data = schema.load(request.get_json())
        logger.info("POST /signup request initiated...")
    except ValidationError as err:
        # return {"erros": err.messages}, 400
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    user_name = data["username"]
    email = data["email"]

    if User.query.filter_by(username=user_name).first():
        logger.warning(f"Signup attempt using existing email {email}")
        return user_already_exists("username already exist")

    if User.query.filter_by(email=email).first():
        logger.warning(f"Signup attempt using existing email {email}")
        return user_already_exists("email already in use")

    try:
        hashed_password = bcrypt.generate_password_hash(data["password"]).decode(
            "utf-8"
        )
        new_user = User(username=user_name, email=email,
                        password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User Created:  username={
                    user_name} user_id={new_user.id}")
        return jsonify({"message": f"{user_name} user created Sucessfully"}), 201

    except Exception as e:
        logger.error(
            f"Error in creating user: username={user_name}\
            email={email} error={e}"
        )
        return internal_server_error()


# this is the most important part because we are generatingt the token , which is necessary for the stateless feature


@main.route("/login", methods=["POST"])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
        logger.info("POST /login requested ...")
    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    if data.get("email"):
        # /one()  we can use that since there will only user with that username
        user = User.query.filter_by(email=data["email"]).first()
        logger.info(f"User used email={data['email']} as the login")
    else:
        logger.info(f"User used username={data['username']}")
        user = User.query.filter_by(username=data["username"]).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        logger.warning(
            f"Failed login attempt: for identifier={
                data['email'] or data['username']
            } from IP={
                request.remote_addr
            } "  # will work if you dont deploy it on the server with reverse proxy nginx,
        )
        return unauthorized_error(msg="Invalid Credentials")

    token = generate_token(user.id)
    # here we have to give the jwt token for future
    if token:
        logger.info("Token is generated")
    return jsonify({"token": token})


@main.route("/tasks", methods=["GET"])
@token_required
def get_tasks_all(user_id):
    tasks = Task.query.filter_by(
        user_id=user_id
    ).all()  # will get all the ask of the user
    logger.info("GET /task requested for get_tasks_all ...")

    if not tasks:
        logger.warning(f"No Task's found with user_id={user_id}")
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
    logger.info("GET /tasks requested for get_task...")

    if not task:
        logger.warning(f"No Task found with task_id = {
                       task_id}, user_id={user_id}")
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
        logger.info("POST /tasks requested for add_task...")

    except ValidationError as err:
        logger.error(f"Input error {err.messages}")

        return handle_marshmallow_error(err)

    if data.get("user_id"):
        # no user_id is required  while adding task , mostly JWT token will get that
        logger.warning(
            "Client providing user_id in payload, which is already been get by token"
        )
        return forbidden_access("Forbidden")

    try:
        new_task = Task(
            title=data["title"],
            description=data.get("description", ""),
            user_id=user_id,
        )
        db.session.add(new_task)
        db.session.commit()

        logger.info(
            f"Task added: task_id={new_task.id}, title={new_task.title}, user_id={
                user_id
            }"
        )

        return jsonify({"message": "Task added", "task_id": new_task.id}), 201
    except Exception as e:
        logger.error(f"Task creation failed error={e}")
        return internal_server_error()


@main.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete(user_id, task_id):
    task = db.session.get(Task, task_id) or abort(404)
    if task.user_id != user_id:
        logger.warning(
            "task user_id doesnt matched with the accessing user_id ,Cant delete other person task !! "
        )
        return forbidden_access("Forbidden,Not authorized to access other")
    db.session.delete(task)
    db.session.commit()
    logger.info(f"Deleted Task: task with task_id={
                task_id} and user_id={user_id}")
    return jsonify({"message": f"Task {id} deleted"})
