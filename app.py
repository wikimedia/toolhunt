from api import create_app

app = create_app()


# @app.route("/")
# def hello():
#   return "Hello, world"

# API access variables and fetch stuff -- will move to another file later
import os
import requests
import flask
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

load_dotenv()

oauth = OAuth(app)
# Note that the name of the env variables needs to match the registered name here
# See authlib documentation for more information
oauth.register(
    name="toolhub",
    access_token_url="https://toolhub-demo.wmcloud.org/o/token/",
    access_token_params=None,
    authorize_url="https://toolhub-demo.wmcloud.org/o/authorize/",
    authorize_params=None,
    api_base_url="https://toolhub-demo.wmcloud.org/api/",
    client_kwargs=None,
)


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

# My goofy test

new_update = {
  "api_url": "https://www.example.com",
  "comment": "First successful test of toolhub's authentication"
}

TOOL_TEST_API_ENDPOINT = "https://toolhub-demo.wmcloud.org/api/tools/"
my_tools = ("testy-mc-test-tool", "special-characters", "special-characters2")


@app.route('/put_test')
def put_test():
  """ Simple put test """
  url = f'{TOOL_TEST_API_ENDPOINT}{my_tools[0]}/annotations/'
  print(url)
  header = {"Authorization": f'Bearer {flask.session["token"]["access_token"]}'}
  response = requests.put(url, data=new_update, headers=header)
  r = response.json()
  return r



