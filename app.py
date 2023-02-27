import subprocess

import flask

from api import create_app, ext_celery, oauth

app = create_app()
celery = ext_celery.celery


# Enable celery auto reloading
def run_worker():
    subprocess.call(["celery", "-A", "app.celery", "worker", "--loglevel=info"])


@app.cli.command("celery_worker")
def celery_worker():
    from watchgod import run_process

    run_process("./api", run_worker)


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
