import flask

from api import create_app, ext, oauth

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
