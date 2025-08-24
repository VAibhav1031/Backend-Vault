from flask_sqlalchemy import SQLAlchemy
from flask_task_manager.config import DevConfig
from flask import Flask
from flask_bcrypt import Bcrypt
import logging.config
from .logging_config import setup_logging
from flask_mail import Mail

db = SQLAlchemy()
bcrypt = Bcrypt()

mail = Mail()


def create_app(config_class=DevConfig, verbose=False, quiet=False, log_to_file=True):
    setup_logging(verbose=verbose, quiet=quiet, log_to_file=log_to_file)

    app = Flask(__name__)
    app.config.from_object(config_class)

    logger = logging.getLogger(__name__)
    logger.info("Flask app created and logging initialized")
    db.init_app(
        app
    )  # this will create the instance to use the flask app outside the main run
    bcrypt.init_app(app)
    mail.init_app(app)

    from flask_task_manager.routes import main

    app.register_blueprint(main)

    return app
