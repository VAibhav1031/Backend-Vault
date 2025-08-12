from flask_task_manager import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    tasks = db.relationship("Tasks", backref="user", lazy=True)


# okay currently if i want to find the tasks for the user as normal way
# i want to write the  query 'Find all tasks where user.id equals id'
# this is okay but with relationship()  function we can acess this way easier
# like user.tasks to list all task belong to the users
# same from the  tasks side we can do  the task.user
# this happend because of the backref
#
#
# backref user is object table created on the Tasks side which
# help in acessing the  task object easier
# you can think it as the  bidirection setup created


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String)
    completion = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
