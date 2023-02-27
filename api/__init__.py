import os

from authlib.integrations.flask_client import OAuth
from celery import current_app as current_celery_app
from flask import Flask
from flask_celeryext import FlaskCeleryExt
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

api = Api()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()

from api.config import config  # noqa
from api.routes import contributions, fields, tasks, user  # noqa


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    api.init_app(app)
    ext_celery.init_app(app)
    db.init_app(app)
    oauth.init_app(app)
    oauth.register(name="toolhub")
    api.register_blueprint(tasks)
    api.register_blueprint(contributions)
    api.register_blueprint(fields)
    api.register_blueprint(user)
    migrate.init_app(app, db)

    return app

def make_celery(app):
    celery = current_celery_app
    celery.config_from_object(app.config, namespace="CELERY")
    return celery

ext_celery = FlaskCeleryExt(create_celery_app=make_celery)