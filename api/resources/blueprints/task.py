from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api import db
from api.resources.schemas import TaskSchema
from api.models import Task

blp = Blueprint("tasks", __name__, description="Fetching and updating Toolhunt tasks")

@blp.route("/api/tasks")
class TaskList(MethodView):
  @blp.response(200, TaskSchema(many=True))
  def get(self):
    return Task.query.filter(Task.user.is_(None)).limit(10)
