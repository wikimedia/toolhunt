from flask.cli import FlaskGroup

from api import db
from app import app

from api.models import Tool, Field, Task
from data import tool_data, field_data, task_data


cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("insert_data")
def insert_data():
    db.session.bulk_insert_mappings(Tool, tool_data)
    db.session.bulk_insert_mappings(Field, field_data)
    db.session.bulk_insert_mappings(Task, task_data)
    db.session.commit()


if __name__ == "__main__":
    cli()