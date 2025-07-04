from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

# Mail Config


mail = Mail(app)

from flaskblog.users.routes import users
from flaskblog.main.routes import main
from flaskblog.posts.routes import posts

app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(posts)
