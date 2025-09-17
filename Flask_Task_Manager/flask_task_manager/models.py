from flask_task_manager import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)

    # id ont think to have the backref for the passwordreset


# okay currently if i want to find the tasks for the user as normal way
# i want to write the  query 'Find all tasks where user.id equals id'
# this is okay but with relationship()  function we can acess this way easier
# like user.tasks to list all task belong to the users
# same from the  tasks side we can do  the task.user
# this happend because of the backref

#
# backref user is object table created on the Tasks side which
# help in acessing the  task object easier
# you can think it as the  bidirection setup created


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text)
    completion = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class PasswordReset(db.Model):
    __tablename__ = "password_resets"

    id = db.Column(db.Integer, primary_key=True)
    reset_token = db.Column(db.String(255), nullable=False)
    expired_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
