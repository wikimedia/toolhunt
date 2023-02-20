from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import desc, text
from api import db
from api.schemas import ContributionArgSchema, ContributionSchema, FieldSchema, ScoreSchema, TaskSchema
from api.models import Field, Task

contributions = Blueprint("contributions", __name__, description="Get information about contributions made using Toolhunt")

@contributions.route("/api/contributions/")
class Contributions(MethodView):
  @contributions.arguments(ContributionArgSchema, location="query", required=False)
  @contributions.response(200, ContributionSchema(many=True))
  def get(self, query_args):
    """Returns contributions made using Toolhunt"""
    if query_args:
      limit = query_args["limit"]
      return Task.query.filter(Task.user.is_not(None)).order_by(desc(Task.timestamp)).limit(int(limit))
    else: 
      return Task.query.filter(Task.user.is_not(None)).order_by(desc(Task.timestamp))

@contributions.route("/api/contributions/<string:user>")
class ContributionsByUser(MethodView):
  @contributions.response(200, ContributionSchema(many=True))
  def get(self, user):
    """Returns contributions by user"""
    # Ideally in the future we could introduce pagination and return all of a user's contributions
    return Task.query.filter(Task.user == user).order_by(desc(Task.timestamp)).limit(10)

@contributions.route("/api/contributions/top-scores")
class ContributionHighScores(MethodView):
  @contributions.response(200, ScoreSchema(many=True))
  def get(self):
    """Returns the most prolific Toolhunters and their scores"""
    query = text("SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL GROUP BY user ORDER BY 2 DESC LIMIT 30")
    results = db.session.execute(query)
    scores = []
    for row in results:
      result = {"user": row[0], "score": row[1]}
      scores.append(result)
    return jsonify(scores)
  

fields = Blueprint("fields", __name__, description="Retrieving information about annotations fields")

@fields.route("/api/fields")
class FieldList(MethodView):
  @fields.response(200, FieldSchema(many=True))
  def get(self):
    return Field.query.all()

@fields.route("/api/fields/<string:name>")
class FieldInformation(MethodView):
  @fields.response(200, FieldSchema)
  def get(self, name):
    return Field.query.get_or_404(name)
  

tasks = Blueprint("tasks", __name__, description="Fetching and updating Toolhunt tasks")

@tasks.route("/api/tasks")
class TaskList(MethodView):
  @tasks.response(200, TaskSchema(many=True))
  def get(self):
    return Task.query.filter(Task.user.is_(None)).limit(10)