import json
from pathlib import Path

from flask.cli import FlaskGroup

from api import db
from api.models import Field, Task
from app import app
from jobs.populate_db import insert_into_db, run_bulk_population_job

cli = FlaskGroup(app)
BASE_DIR = app.config["BASE_DIR"]


@cli.command("insert_fields")
def insert_fields():
    """Insert data about annotations fields into the DB"""
    with open(Path(f"{BASE_DIR}/tests/fixtures/fields.json")) as fields:
        field_data = json.load(fields)
        db.session.bulk_insert_mappings(Field, field_data)
        db.session.commit()


@cli.command("run_population_job")
def run_population_job():
    """Fetches and inserts tool data from Toolhub"""
    run_bulk_population_job()


@cli.command("run_test_population")
def run_populate_db_test():
    """Inserts the test tool and task data into db"""
    with open(Path(f"{BASE_DIR}/tests/fixtures/data.json")) as data:
        test_data = json.load(data)
        test_tool_data = test_data[0]["tool_data"]
        insert_into_db(test_tool_data)
        test_task_data = test_data[1]["task_data"]
        db.session.bulk_insert_mappings(Task, test_task_data)
        db.session.commit()


if __name__ == "__main__":
    cli()
