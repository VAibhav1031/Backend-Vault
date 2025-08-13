from flask_sqlalchemy import SQLAlchemy
from flask_task_manager.config import DevConfig
from flask import Flask


db = SQLAlchemy()


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(
        app
    )  # this will create the instance to use the flask app outside the main run

    from flask_task_manager.routes import main

    app.register_blueprint(main)

    return app
