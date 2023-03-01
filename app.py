import flask

from api import create_app, ext, oauth
from api.utils import ToolhubClient

# from flask_celeryext import RequestContextTask


app = create_app()
celery = ext.celery


@app.route("/")
def index():
    return "Hello world"


@app.route("/api/login")
def login():
    """Initiate OAuth handshake with Toolhub."""
    return oauth.toolhub.authorize_redirect(app.config["REDIRECT_URI"])


@app.route("/api/authorize")
def authorize():
    """Handle OAuth callback from Toolhub."""
    flask.session["token"] = oauth.toolhub.authorize_access_token()
    return flask.redirect("/")


@app.route("/api/logout")
def logout():
    """Clear session and redirect to /."""
    flask.session.clear()
    return flask.redirect("/")


@celery.task
def divide(x, y):
    import time

    time.sleep(5)
    return x / y


@celery.task()
def make_put_request(name_string, data_obj, token):
    from app import app

    toolhub_client = ToolhubClient(app.config["TOOLHUB_API_ENDPOINT"])
    toolhub_client.put_celery(name_string, data_obj, token)


@celery.task()
def make_get_request(name_string):
    from app import app

    toolhub_client = ToolhubClient(app.config["TOOLHUB_API_ENDPOINT"])
    toolhub_client.get_celery(name_string)
    