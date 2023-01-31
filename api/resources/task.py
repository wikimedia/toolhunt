from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api.resources.db import db
from api.resources.schemas import TaskSchema
from api.models import Task

blp = Blueprint("task", __name__, description="Operations on Toolhunt tasks")

@blp.route("/api/task")
class TaskList(MethodView):
  @blp.response(200, TaskSchema(many=True))
  def get(self):
    return Task.query.all()