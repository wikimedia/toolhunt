import os
from pathlib import Path

class BaseConfig:
  """Base config"""
  BASE_DIR = Path(__file__).parent.parent
  TESTING = False
  SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
  SQLALCHEMY_TRACK_MODIFICATIONS = False

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