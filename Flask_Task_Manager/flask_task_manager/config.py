import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///task.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
