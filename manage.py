import json
from flask.cli import FlaskGroup
from api import db
from app import app
from api.models import Task
from jobs.populate_db import insert_fields, get_tools, populate_db


cli = FlaskGroup(app)

@cli.command("insert_fields")
def run_field_insert():
    """ Inserts field data """
    insert_fields()

@cli.command("populate_db_initial")
def run_populate_db():
    """ Fetches and inserts tool data from Toolhub """
    tool_data = get_tools()
    populate_db(tool_data)

@cli.command("populate_db_test")
def run_populate_db_test():
    """ Inserts the test tool and task data into db """
    BASE_DIR = app.config["BASE_DIR"]
    with open(f'{BASE_DIR}/tests/fixtures/data.json') as data:
        test_data = json.load(data)
        test_tool_data = test_data[0]["tool_data"]
        populate_db(test_tool_data)
        test_task_data = test_data[1]["task_data"]
        db.session.bulk_insert_mappings(Task, test_task_data)
        db.session.commit()

if __name__ == "__main__":
    cli()