from api import db

class Tool(db.Model):
  __tablename__ = "tool"
  __table_args__ = {"mysql_charset": "utf8mb4"}

  name = db.Column(db.String(255), primary_key=True, nullable=False)
  title = db.Column(db.String(255), nullable=False)
  description = db.Column(db.TEXT(65535), nullable=False)
  url = db.Column(db.String(2047), nullable=False)
  tasks = db.relationship("Task", backref="tool", lazy="dynamic")
  # repository = db.Column(db.String(2047), nullable=True)
