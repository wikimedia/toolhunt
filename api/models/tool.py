from api.resources.db import db

class Tool(db.Model):
  __tablename__ = "tool"

  name = db.Column(db.String(120), primary_key=True, nullable=False)
  title = db.Column(db.String(120), nullable=False)
  description = db.Column(db.String(2047), nullable=False)
  url = db.Column(db.String(2047), nullable=False)
  tasks = db.relationship("Task", backref="tool", lazy="dynamic")
  # repository = db.Column(db.String(2047), nullable=True)
