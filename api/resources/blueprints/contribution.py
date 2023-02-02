from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import desc, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api import db
from api.resources.schemas import ContributionSchema, ScoreSchema
from api.models import Task

blp = Blueprint("contributions", __name__, description="Get information about contributions made using Toolhunt")


@blp.route("/api/contributions/")
class Contributions(MethodView):
  @blp.response(200, ContributionSchema(many=True))
  def get(self):
    """Returns all contributions"""
    return Task.query.filter(Task.user.is_not(None))

@blp.route("/api/contributions/latest")
class ContributionsLatest(MethodView):
  @blp.response(200, ContributionSchema(many=True))
  def get(self):
    """Returns the 10 most recent contributions"""
    return Task.query.filter(Task.user.is_not(None)).order_by(desc(Task.timestamp)).limit(10)

@blp.route("/api/contributions/<string:user>")
class ContributionsByUser(MethodView):
  @blp.response(200, ContributionSchema(many=True))
  def get(self, user):
    """Returns contributions by user"""
    return Task.query.filter(Task.user == user).order_by(desc(Task.timestamp)).limit(10)

  # Ideally in the future we could introduce pagination and return all of a user's contributions

@blp.route("/api/contributions/scores")
class ContributionHighScores(MethodView):
  @blp.response(200, ScoreSchema(many=True))
  def get(self):
    """Returns the most prolific Toolhunters and their scores"""
    query = text("SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL GROUP BY user ORDER BY 2 DESC LIMIT 30")
    results = db.session.execute(query)
    scores = []
    for row in results:
      result = {"user": row[0], "score": row[1]}
      scores.append(result)
    return jsonify(scores)
