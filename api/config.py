import os
from pathlib import Path

class BaseConfig:
  """Base config"""
  BASE_DIR = Path(__file__).parent.parent
  TESTING = False
  SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  API_TITLE = "Toolhunt REST API"
  API_VERSION = "v1"
  OPENAPI_VERSION = "3.0.3"
  OPENAPI_URL_PREFIX = "/"
  OPENAPI_SWAGGER_UI_PATH = "/api/documentation"
  OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
  PROPAGATE_EXCEPTIONS = True

class DevelopmentConfig(BaseConfig):
  """Development config"""
  DEBUG = True

class ProductionConfig(BaseConfig):
  """Production config"""
  DEBUG = False

config = {
  "development": DevelopmentConfig,
  "production": ProductionConfig
}