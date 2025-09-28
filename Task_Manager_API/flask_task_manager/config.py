import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    USE_FAKE_MAIL = False
    # use this only when we are developing or testing soemthing

    #####################
    # Mail Config
    #####################
    MAIL_SERVER = "smtp.googlemail.com"  # currently we are using the smptp relay
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class DevConfig(Config):
    ###################################
    # DB_configs (taken from env file)
    ###################################

    DB_USER = os.environ.get("DEV_DB_USER")
    DB_PASSWORD = os.environ.get("DEV_DB_PASSWORD")
    DB_HOST = os.environ.get("DEV_DB_HOST")
    DB_PORT = os.environ.get("DEV_DB_PORT")
    DB_NAME = os.environ.get("DEV_DB_NAME")

    ###################################
    # SQLAlchemy config
    ##################################

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    USE_FAKE_MAIL = True
    DEBUG = True


class ProdConfig(Config):
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
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY must be setup in the  .env file for the  production"
        )

    DEBUG = False


class TestConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = "sqlite:///:memory:"

    USE_FAKE_MAIL = True
    DEBUG = True


config = {
    "development": DevConfig,
    "production": ProdConfig,
    "testing": TestConfig,
    "default": DevConfig,
}


def get_config(config_name=None):
    # it will first go and check the .env  if it has the FLASK_ENV or not
    # then it will proceed to the  to return
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    return config.get(config_name, DevConfig)
