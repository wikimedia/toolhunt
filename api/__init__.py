import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from api.config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
  if config_name is None:
    config_name = os.environ.get("FLASK_CONFIG", "development")
  
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  db.init_app(app)
  # migrate.init_app(app, db)

  return app
