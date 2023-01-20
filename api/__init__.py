import os

from flask import Flask

from api.config import config

def create_app(config_name=None):
  if config_name is None:
    config_name = os.environ.get("FLASK_CONFIG", "development")

  app = Flask(__name__)

  app.config.from_object(config[config_name])

  return app

# I have left out the SQLAlchemy, DB and Migration related code for the moment
