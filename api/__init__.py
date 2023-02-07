import os

from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api 
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

from api.resources.blueprints.task import blp as TaskBlueprint
from api.resources.blueprints.contribution import blp as ContributionBlueprint
from api.config import config

def create_app(config_name=None):
  if config_name is None:
    config_name = os.environ.get("FLASK_CONFIG", "development")
  
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  api = Api(app)
  db.init_app(app)
  api.register_blueprint(TaskBlueprint)
  api.register_blueprint(ContributionBlueprint)
  migrate.init_app(app, db)


  return app