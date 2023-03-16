from api import db


class Tool(db.Model):
    __tablename__ = "tool"
    __table_args__ = {"mysql_charset": "binary"}

    name = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.TEXT(65535), nullable=False)
    url = db.Column(db.String(2047), nullable=False)
    tasks = db.relationship("Task", backref="tool", lazy="dynamic")
    last_updated = db.Column(db.DateTime, nullable=False)


class Field(db.Model):
    __tablename__ = "field"
    __table_args__ = {"mysql_charset": "binary"}

    name = db.Column(db.String(80), primary_key=True, nullable=False)
    description = db.Column(db.String(2047), nullable=False)
    tasks = db.relationship("Task", backref="field", lazy="dynamic")
    input_options = db.Column(db.String(2047), nullable=True)
    pattern = db.Column(db.String(320), nullable=True)


class Task(db.Model):
    __tablename__ = "task"
    __table_args__ = {"mysql_charset": "binary"}

    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(255), db.ForeignKey("tool.name"), nullable=False)
    field_name = db.Column(db.String(80), db.ForeignKey("field.name"), nullable=False)
    last_attempted = db.Column(db.DateTime, nullable=True)


class CompletedTask(db.Model):
    __tablename__ = "completed_task"
    __table_args__ = {"mysql_charset": "binary"}

    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(255), nullable=False)
    tool_title = db.Column(db.String(255), nullable=False)
    field = db.Column(db.String(80), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    completed_date = db.Column(db.DateTime, nullable=False)
