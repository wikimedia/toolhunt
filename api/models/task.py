from datetime import datetime
from api.resources.db import db

class Task(db.Model):
  __tablename__ = "task"

  id = db.Column(db.Integer, primary_key=True)
  tool_name = db.Column(db.String(80), db.ForeignKey("tool.name"), nullable=False)
  # tool = db.relationship("Tool", back_populates="task", lazy="dynamic")
  field_name = db.Column(db.String(80), db.ForeignKey("field.name"), nullable=False)
  # field = db.relationship("Field", back_populates="task", lazy="dynamic")
  user = db.Column(db.String(128), nullable=True)
  timestamp = db.Column(db.DateTime, nullable=True)