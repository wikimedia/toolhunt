import flask
import datetime
import requests
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import desc, text
from api import db
from api.schemas import ContributionLimitSchema, ContributionSchema, FieldSchema, ScoreSchema, ScoreLimitSchema, TaskSchema, TaskCompleteSchema, UserSchema
from api.models import Field, Task

contributions = Blueprint("contributions", __name__, description="Get information about contributions made using Toolhunt")

@contributions.route("/api/contributions/")
class Contributions(MethodView):
  @contributions.arguments(ContributionLimitSchema, location="query", required=False)
  @contributions.response(200, ContributionSchema(many=True))
  def get(self, query_args):
    """Return contributions made using Toolhunt."""
    if query_args:
      limit = query_args["limit"]
      return Task.query.filter(Task.user.is_not(None)).order_by(desc(Task.timestamp)).limit(int(limit))
    else: 
      return Task.query.filter(Task.user.is_not(None)).order_by(desc(Task.timestamp))

@contributions.route("/api/contributions/<string:user>")
class ContributionsByUser(MethodView):
  @contributions.response(200, ContributionSchema(many=True))
  def get(self, user):
    """Return contributions by user."""
    # Ideally in the future we could introduce pagination and return all of a user's contributions
    return Task.query.filter(Task.user == user).order_by(desc(Task.timestamp)).limit(10)

@contributions.route("/api/contributions/top-scores")
class ContributionHighScores(MethodView):
  @contributions.arguments(ScoreLimitSchema, location="query", required=False)
  @contributions.response(200, ScoreSchema(many=True))
  def get(self, query_args):
    """Return the most prolific Toolhunters and their scores."""
    if query_args:
      today = datetime.datetime.now(datetime.timezone.utc)
      day_count = query_args["since"]
      end_date = today - datetime.timedelta(days = day_count)
      print(end_date)
      scores_query = text("SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL AND timestamp >= :date GROUP BY user ORDER BY 2 DESC LIMIT 30").bindparams(date=end_date)
      scores = get_scores(scores_query)
      return scores
    else: 
      scores_query = text("SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL GROUP BY user ORDER BY 2 DESC LIMIT 30")
      scores = get_scores(scores_query)
      return scores

def get_scores(scores_query):
    """Insert score data into a list of dicts and return."""
    results = db.session.execute(scores_query)
    scores = []
    for row in results:
      result = {"user": row[0], "score": row[1]}
      scores.append(result)
    return scores
  

fields = Blueprint("fields", __name__, description="Retrieving information about annotations fields")

@fields.route("/api/fields")
class FieldList(MethodView):
  @fields.response(200, FieldSchema(many=True))
  def get(self):
    "Return all annotations field data."
    return Field.query.all()

@fields.route("/api/fields/<string:name>")
class FieldInformation(MethodView):
  @fields.response(200, FieldSchema)
  def get(self, name):
    "Return data about a specific annotations field."
    return Field.query.get_or_404(name)
  

tasks = Blueprint("tasks", __name__, description="Fetching and updating Toolhunt tasks")

@tasks.route("/api/tasks")
class TaskList(MethodView):
  @tasks.response(200, TaskSchema(many=True))
  def get(self):
    "Return a bundle of 10 incomplete tasks."
    return Task.query.filter(Task.user.is_(None)).limit(10)
  
@tasks.route("/api/tasks/<string:task_id>")
class TaskById(MethodView):
  @tasks.response(200, TaskSchema)
  def get(self, task_id):
    "Return information about a specific task."
    task = Task.query.get_or_404(task_id)
    return task
  
  @tasks.arguments(TaskCompleteSchema)
  @tasks.response(201)
  def put(self, task_data, task_id):
    """Update a tool record on Toolhub."""
    task = Task.query.get_or_404(task_id)
    if task and task.tool_name == task_data["tool"] and task.field_name == task_data["field"]:
      if task.user != None:
        return "This task has already been completed."
      elif flask.session and flask.session["token"]:
        tool = task_data["tool"]
        data_obj = build_request(task_data)
        result = put_to_toolhub(tool, data_obj)
        if result == 200:
          username = get_current_user()
          task.user = username
          task.timestamp = datetime.datetime.now(datetime.timezone.utc)
          db.session.add(task)
          try:
            db.session.commit()
            return f'{task_data["field"]} successfully updated for {tool}.'
          except:
            return "Updating our db didn't work."
        else:
          return "Inserting the data into Toolhub didn't work." 
      else:
        return "User must be logged in to update a tool."
    else:
      return "The data doesn't match the specified task."

def build_request(task_data):
  """Take data and return an object to PUT to Toolhub"""
  field = task_data["field"]
  value = task_data["value"]
  comment = f'Updated {field} using Toolhunt'
  data = {}
  data[field] = value
  data["comment"] = comment
  return data

def get_current_user():
  """Get the username of currently logged-in user."""
  # Importing the oauth early results in an error 
  # Will fix this once I've dealt with T330263
  from app import oauth
  if not flask.session:
    abort(401, message="No user is currently logged in.")
  else: 
      try: 
        resp = oauth.toolhub.get("user/", token=flask.session["token"])
        print(resp, "This is from the function")
        resp.raise_for_status()
        profile = resp.json()
        username = profile["username"]
        return username
      except requests.exceptions.HTTPError as err:
        print(err)
        abort(401, message="User authorization failed.")
      except requests.exceptions.ConnectionError as err:
        print(err)
        abort(503, message="Server connection failed.  Please try again.")
      except requests.exceptions.RequestException as err:
        print(err)
        abort(501, message="Server encountered an unexpected error.")

  
def put_to_toolhub(tool, data):
  """Take request data from the frontend and make a PUT request to Toolhub."""
  TOOL_TEST_API_ENDPOINT = "https://toolhub-demo.wmcloud.org/api/tools/"
  url = f'{TOOL_TEST_API_ENDPOINT}{tool}/annotations/'
  header = {"Authorization": f'Bearer {flask.session["token"]["access_token"]}'}
  response = requests.put(url, data=data, headers=header)
  r = response.status_code
  return r

user = Blueprint("user", __name__, description="Get information about the currently logged-in user.")

@user.route("/api/user")
class CurrentUser(MethodView):
  @tasks.response(200, UserSchema)
  def get(self):
    """Get the username of currently logged-in user."""
    response = get_current_user()
    if type(response) == str:
      username = {"username": response}
      return username
    else:
      return response
