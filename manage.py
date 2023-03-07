import json

from flask.cli import FlaskGroup

from api import db
from api.models import Task
from api.utils import ToolhubClient
from app import app
from jobs.populate_db import insert_fields, bulk_population_job, insert_into_db

cli = FlaskGroup(app)
toolhub_client = ToolhubClient(app.config["TOOLHUB_API_ENDPOINT"])


@cli.command("insert_fields")
def run_field_insert():
    """Inserts field data"""
    insert_fields()


@cli.command("run_population_job")
def run_population_job():
    """Fetches and inserts tool data from Toolhub"""
    bulk_population_job()


@cli.command("run_test_population")
def run_populate_db_test():
    """Inserts the test tool and task data into db"""
    BASE_DIR = app.config["BASE_DIR"]
    with open(f"{BASE_DIR}/tests/fixtures/data.json") as data:
        test_data = json.load(data)
        test_tool_data = test_data[0]["tool_data"]
        insert_into_db(test_tool_data)
        test_task_data = test_data[1]["task_data"]
        db.session.bulk_insert_mappings(Task, test_task_data)
        db.session.commit()


if __name__ == "__main__":
    cli()
