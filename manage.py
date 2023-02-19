from flask.cli import FlaskGroup
from api import db
from app import app
from api.models import Tool, Task
from tests.fixtures.data import tool_data, task_data
from jobs.populate_db import insert_fields, populate_db


cli = FlaskGroup(app)

@cli.command("insert_mock_data")
def insert_mock_data():
    """ Inserts the mock tasks and tools """
    db.session.bulk_insert_mappings(Tool, tool_data)
    db.session.bulk_insert_mappings(Task, task_data)
    db.session.commit()

@cli.command("insert_fields")
def run_field_insert():
    """ Inserts field data """
    insert_fields()

@cli.command("populate_db")
def run_populate_db():
    """ Fetches and inserts tool data from Toolhub """
    populate_db()


if __name__ == "__main__":
    cli()