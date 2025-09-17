from flask import Blueprint, jsonify, request, abort
from flask_task_manager import db
from .models import Task

from .utils import (
    token_required,
    cursor_encoder,
    cursor_decoder,
)
from .error_handler import (
    handle_marshmallow_error,
    not_found,
    internal_server_error,
    forbidden_access,
    bad_request,
)
from flask_task_manager.schemas import (
    AddUpdateTask,
    ValidationError,
)
import logging
import datetime
from sqlalchemy import and_

DEFAULT_LIMIT = 10
MAX_LIMIT = 100

tasks = Blueprint("tasks", __name__, url_prefix="/api/")

logger = logging.getLogger(__name__)


def filter_manager(completion, title, after_str, before_str, query):
    try:
        if after_str:
            # It is  still object which is return but that object has peice of info that will use when  compare in query
            # Z is stand for the 'ZULU' which is bit common for the military and all and normal use also , python library doesnt have any way
            # to handle that or something so we replace that thing with notrmal one s
            after = datetime.fromisoformat(after_str.replace("Z", "+00:00"))
        if before_str:
            before = datetime.fromisoformat(before_str.replace("Z", "+00:00"))

    except Exception as e:
        logger.error(
            f"Invalid datetime format {e}, Use ISO 8601 UTC , eg 2025-09-11T18:30:00Z"
        )
        return bad_request(
            msg="Invalid Datetime",
            details=f"Invalid datetime format {
                e
            }, Use ISO 8601 UTC , eg 2025-09-11T18:30:00Z",
        )

    if completion is not None:
        normalized = completion.lower()
        if normalized in ("true", "1", "yes"):
            query = query.filter(Task.completion == True)
        elif normalized in ("false", "0", "no"):
            query = query.filter(Task.completion == False)

    # postgres based
    # if title is not None:
    #     query = query.filter(Task.title.ilike(f"%{title}%"))

    if title:
        query = query.filter(Task.title == title)

    if after and before:
        query = query.filter(and_(Task.created_at >= after, Task.created_at <= before))
    elif after:
        query = query.filter(Task.created_at >= after)

    elif before:
        query = query.filter(Task.created_at <= before)

    return query


@tasks.route("/tasks", methods=["GET"])
@token_required
def get_tasks_all(user_id):
    try:
        query = Task.query.filter_by(user_id=user_id).order_by(Task.id.asc())
        logger.info("GET /api/tasks requested for get_tasks_all ...")

        ###################################
        # Custom arguments for 'filter-ing'
        # #################################
        try:
            query = filter_manager(
                request.args.get("completion"),
                request.args.get("title"),
                request.args.get("after"),
                request.args.get("before"),
            )

        except Exception as e:
            return internal_server_error(msg=f"{e}")

        #####################################
        # Cursor Pagination control area ....
        #####################################
        try:
            cursor = request.args.get("cursor")
            limit = int(request.args.get("limit", DEFAULT_LIMIT))
            page_size = min(limit, MAX_LIMIT)

            if cursor:
                cursor_decoded_id = cursor_decoder(cursor)
                query = query.filter(Task.id > cursor_decoded_id)

            # +1 for has_more  check
            results = query.limit(page_size + 1).all()

            # debugging logger
            logger.info(f"results  of he tasks : {results}")

            if not results:
                logger.error(f"No Task's found with user_id={user_id}")
                logger.info(f"Final query was : {query}")
                return not_found("No Task found")

            has_more = len(results) > page_size
            tasks = results[:page_size]

            # bit more  clearity i would sayy
            next_cursor = None
            if has_more and len(tasks) > 0:
                next_id = tasks[-1].id
                next_cursor = cursor_encoder(next_id)

            # next_cursor = (
            #     cursor_encoder(tasks[-1].id) if has_more and len(tasks) > 0 else None
            # )
            #
            # we have the  few things to be remeber

            # tasks = query.  # default for every
            # # Debugging logger
            # logger.info(f"before 404 check : {[t.title for t in tasks]}")

            return jsonify(
                {
                    "data": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "completion": t.completion,
                            "created_at": t.created_at,
                        }
                        for t in tasks
                    ],
                    "pagination": {
                        "next_cursor": next_cursor,
                        "has_more": has_more,
                        "limit": page_size,
                        "total_returned": len(tasks),
                    },
                    "meta": {"version": "1.0"},
                }
            )

        except Exception as e:
            logger.error(f"No cursor : {e}")

    except Exception as e:
        logger.error(f"Error ocurred in the /tasks route : {e}")
        return internal_server_error()


@tasks.route("/tasks/<int:task_id>", methods=["GET"])
@token_required
def get_task(user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    logger.info("GET /api/tasks requested for get_task...")

    if not task:
        logger.error(f"No Task found with task_id = {task_id}, user_id={user_id}")
        return not_found("No Task found")
    return jsonify(
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completion": task.completion,
            "created_at": task.created_at,
        }
    )


@tasks.route("/task/<int:task_id>", methods=["PUT"])
@token_required
def update_task(user_id, task_id):
    schema = AddUpdateTask()
    try:
        data = schema.load(request.get_json())
        logger.info("PUT /task/task_id requested for update_task")

    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        logger.error(
            f"No Task found with \
        task_id={task_id} , user_id={user_id}"
        )
        return not_found("No Task found")

    try:
        task.title = data["title"]
        task.description = data["description"]
        db.session.commit()

    except Exception as e:
        logger.error(
            f"Error in updating the task: user_id={user_id}"
            f"task_id={task_id} with error={e}"
        )
        internal_server_error()


@tasks.route("/tasks", methods=["POST"])
@token_required
def add_task(user_id):
    schema = AddUpdateTask()
    try:
        data = schema.load(request.get_json())
        logger.info("POST /api/tasks requested for add_task...")

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
            completion=data.get("completion", False),
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


@tasks.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete(user_id, task_id):
    task = db.session.get(Task, task_id) or abort(404)
    if task.user_id != user_id:
        logger.warning(
            f"task user_id doesnt match token user_id : user_id = {
                user_id
            }, task.user_id={task.user_id} "
        )
        return forbidden_access("Forbidden,Not authorized to access other Data")
    db.session.delete(task)
    db.session.commit()
    logger.info(f"Deleted Task: task with task_id={task_id}and user_id={user_id}")
    return jsonify({"message": f"Task {id} deleted"})


@tasks.route("/tasks", methods=["DELETE"])
@token_required
def delete_all(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    logger.info("DELETE /task requested...")

    if not tasks:
        logger.error(f"No Task found out with user_id = {user_id}")
        return not_found("No Task Found")

    for t in tasks:
        db.session.delete(t)

    db.session.commit()

    return jsonify({"message": f"All task of user_id {user_id} deleted "}), 200
