import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    USE_FAKE_MAIL = False
    # use this only when we are developing or testing soemthing

    ###################################
    # DB_configs (taken from env file)
    ###################################

    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")

    ###################################
    # SQLAlchemy config
    ##################################

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    #####################
    # Mail Config
    #####################
    MAIL_SERVER = "smtp.googlemail.com"  # currently we are using the smptp relay
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class DevConfig(Config):
    USE_FAKE_MAIL = True
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
