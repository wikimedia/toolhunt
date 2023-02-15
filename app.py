import flask
from authlib.integrations.flask_client import OAuth
from api import create_app

app = create_app()

oauth = OAuth(app)
oauth.register(name="toolhub")

@app.route("/")
def index():
  """Home screen."""
  ctx = {
      "profile": None,
  }
  if "token" in flask.session:
    resp = oauth.toolhub.get("user/", token=flask.session["token"])
    resp.raise_for_status()
    ctx["profile"] = resp.json()
  return flask.render_template("home.html", **ctx)

@app.route("/login")
def login():
    """Initiate OAuth handshake with Toolhub."""
    redirect_uri = flask.url_for("authorize", _external=True)
    return oauth.toolhub.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
    """Handle OAuth callback from Toolhub."""
    flask.session["token"] = oauth.toolhub.authorize_access_token()
    return flask.redirect("/")

@app.route("/logout")
def logout():
    """Clear session and redirect to /."""
    flask.session.clear()
    return flask.redirect("/")