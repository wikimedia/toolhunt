from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api import db
from api.resources.schemas import FieldSchema
from api.models import Field

blp = Blueprint("fields", __name__, description="Retrieving information about annotations fields")

@blp.route("/api/fields")
class FieldList(MethodView):
  @blp.response(200, FieldSchema(many=True))
  def get(self):
    return Field.query.all()

@blp.route("/api/fields/<string:name>")
class FieldInformation(MethodView):
  @blp.response(200, FieldSchema)
  def get(self, name):
    return Field.query.get_or_404(name)
