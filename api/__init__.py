import os
from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api 
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

from api.routes import fields, contributions, tasks, user
from api.config import config

def create_app(config_name=None):
  if config_name is None:
    config_name = os.environ.get("FLASK_CONFIG", "development")
  
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  api = Api(app)
  db.init_app(app)
  api.register_blueprint(tasks)
  api.register_blueprint(contributions)
  api.register_blueprint(fields)
  api.register_blueprint(user)
  migrate.init_app(app, db)


  return app