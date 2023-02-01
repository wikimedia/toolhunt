from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api import db
from api.resources.schemas import UserSchema
from api.models import UserModel

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/users")
class UserList(MethodView):
  @blp.response(200, UserSchema(many=True))
  def get(self):
    return UserModel.query.all()
  
  @blp.arguments(UserSchema)
  @blp.response(201, UserSchema)
  def post(self, user_data):
    user = UserModel(**user_data)
    try:
      db.session.add(user)
      db.session.commit()
    except IntegrityError:
      abort(400, message="A user with that name already exists.")
    except SQLAlchemyError:
      abort(500, message="An error occurred while creating the user.")
    
    return user