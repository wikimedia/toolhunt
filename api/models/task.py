from datetime import datetime
from api import db

class Task(db.Model):
  __tablename__ = "task"

  id = db.Column(db.Integer, primary_key=True)
  tool_name = db.Column(db.String(80), db.ForeignKey("tool.name"), nullable=False)
  field_name = db.Column(db.String(80), db.ForeignKey("field.name"), nullable=False)
  user = db.Column(db.String(128), nullable=True)
  timestamp = db.Column(db.DateTime, nullable=True)