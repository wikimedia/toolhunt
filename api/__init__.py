import os

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from api.utils import ToolhubClient

api = Api()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
thc = ToolhubClient()

from api.config import config  # noqa
from api.routes import contributions, fields, tasks, user  # noqa


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    api.init_app(app)
    db.init_app(app)
    thc.init_app(app)
    oauth.init_app(app)
    oauth.register(name="toolhub")
    api.register_blueprint(tasks)
    api.register_blueprint(contributions)
    api.register_blueprint(fields)
    api.register_blueprint(user)
    migrate.init_app(app, db)

    return app
