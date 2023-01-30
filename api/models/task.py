from datetime import datetime
from api.resources.db import db

class Task(db.Model):
  __tablename__ = "task"

  id = db.Column(db.Integer, primary_key=True)
  tool = db.Column(db.String(80), db.ForeignKey("tools.name"), nullable=False)
  task = db.Column(db.String(80), db.ForeignKey("task_types.name"), nullable=False)
  user = db.Column(db.String(128), nullable=True)
  timestamp = db.Column(db.DateTime, nullable=True)