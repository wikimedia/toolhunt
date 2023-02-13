from datetime import datetime
from api import db

class Task(db.Model):
  __tablename__ = "task"
  __table_args__ = {"mysql_charset": "utf8mb4"}

  id = db.Column(db.Integer, primary_key=True)
  tool_name = db.Column(db.String(255), db.ForeignKey("tool.name"), nullable=False)
  field_name = db.Column(db.String(80), db.ForeignKey("field.name"), nullable=False)
  user = db.Column(db.String(255), nullable=True)
  timestamp = db.Column(db.DateTime, nullable=True)