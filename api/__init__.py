import os

from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api 
from api.resources.user import blp as UserBlueprint
from api.resources.task import blp as TaskBlueprint
from api.resources.db import db
from api.config import config

migrate = Migrate()


def create_app(config_name=None):
  if config_name is None:
    config_name = os.environ.get("FLASK_CONFIG", "development")
  
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  api = Api(app)
  db.init_app(app)
  api.register_blueprint(UserBlueprint)
  api.register_blueprint(TaskBlueprint)
  migrate.init_app(app, db)


  return app