from flask import Blueprint, jsonify, request
from flask_task_manager import db
from flask_task_manager.models import Task


main = Blueprint("main", __name__)


@main.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()

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


@main.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        user_id=data["user_id"],
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added", "task_id": new_task.id}), 201


@main.route("/tasks/<int:id>", methods=["DELETE"])
def delete(id):
    # this will get me the object of the Tasks
    task = Task.query.get_or_404(id)
    # now i have to delete the  particular associated with the id
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task {id} deleted"})
