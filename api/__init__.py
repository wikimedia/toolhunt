import os

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_celeryext import FlaskCeleryExt
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from api.config import BaseConfig, config

api = Api()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
ext = FlaskCeleryExt()


def create_app():
    config_name = os.environ.get("FLASK_CONFIG", "development")
    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config[config_name])

        api.init_app(app)
        ext.init_app(app)
        db.init_app(app)
        oauth.init_app(app)
        oauth.register(
            name=BaseConfig.TOOLHUB_OAUTH_NAME,
            access_token_url=BaseConfig.TOOLHUB_ACCESS_TOKEN_URL,
            access_token_params=None,
            authorize_url=BaseConfig.TOOLHUB_AUTHORIZE_URL,
            authorize_params=None,
            api_base_url=BaseConfig.TOOLHUB_API_BASE_URL,
            client_kwargs=None,
        )
        # register blueprints
        from api.routes import contributions, fields, metrics, tasks, user  # noqa

        api.register_blueprint(tasks)
        api.register_blueprint(contributions)
        api.register_blueprint(fields)
        api.register_blueprint(metrics)
        api.register_blueprint(user)
        migrate.init_app(app, db)

    return app
