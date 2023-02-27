import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base config"""

    BASE_DIR = Path(__file__).parent.parent
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"
    )
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TITLE = "Toolhunt REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/api/documentation"
    OPENAPI_SWAGGER_UI_URL = (
        "https://tools-static.wmflabs.org/cdnjs/ajax/libs/swagger-ui/4.15.5/"
    )
    PROPAGATE_EXCEPTIONS = True

    # OAuth
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        default=os.urandom(128).decode("utf8", errors="ignore"),
    )
    SERVER_NAME = os.getenv("SERVER_NAME", default="localhost:5000")
    TOOLHUB_CLIENT_ID = os.getenv("TOOLHUB_CLIENT_ID")
    TOOLHUB_CLIENT_SECRET = os.getenv("TOOLHUB_CLIENT_SECRET")
    TOOLHUB_ACCESS_TOKEN_URL = os.getenv(
        "TOOLHUB_ACCESS_TOKEN_URL", default="https://toolhub-demo.wmcloud.org/o/token/"
    )
    TOOLHUB_AUTHORIZE_URL = os.getenv(
        "TOOLHUB_AUTHORIZE_URL", default="https://toolhub-demo.wmcloud.org/o/authorize/"
    )
    TOOLHUB_API_BASE_URL = os.getenv(
        "TOOLHUB_API_BASE_URL", default="https://toolhub-demo.wmcloud.org/api/"
    )
    REDIRECT_URI = os.getenv(
        "REDIRECT_URI", default="http://localhost:8082/api/authorize"
    )


class DevelopmentConfig(BaseConfig):
    """Development config"""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production config"""

    DEBUG = False


config = {"development": DevelopmentConfig, "production": ProductionConfig}
