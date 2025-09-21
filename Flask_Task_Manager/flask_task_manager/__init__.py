from flask_sqlalchemy import SQLAlchemy
from flask_task_manager.config import get_config
from flask import Flask
from flask_bcrypt import Bcrypt
import logging.config
from .logging_config import setup_logging
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()


def create_app(config_class=None, verbose=False, quiet=False, log_to_file=True):
    setup_logging(verbose=verbose, quiet=quiet, log_to_file=log_to_file)

    app = Flask(__name__)
    # here we are creating dynamic attribute
    app.config.from_object(get_config())

    logger = logging.getLogger(__name__)
    logger.info("Flask app created and logging initialized")

    db.init_app(
        app
    )  # this will create the instance to use the flask app outside the main run
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    if app.config.get("USE_FAKE_MAIL", False):
        from flask_task_manager.mail_service.fake_service import FakeMailService

        app.mail_service = FakeMailService(app)

    else:
        from flask_task_manager.mail_service.real_service import RealMailService

        app.mail_service = RealMailService(app)

    from flask_task_manager.auth.routes import auth
    from flask_task_manager.tasks.routes import tasks

    app.register_blueprint(auth)
    app.register_blueprint(tasks)

    return app
