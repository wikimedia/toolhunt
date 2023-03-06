import datetime

from celery import shared_task
from flask import current_app
from sqlalchemy import exc

from api import db
from api.models import Task
from api.utils import ToolhubClient


@shared_task(bind=True)
def make_put_request(self, tool_name, submission_data, token):
    """Create a PUT task using Celery and ToolhubClient."""
    toolhub_client = ToolhubClient(current_app.config["TOOLHUB_API_ENDPOINT"])
    try:
        result = toolhub_client.put(tool_name, submission_data, token)
    except Exception as e:
        print(f"Exception {e} raised, retrying after 5 seconds...")
        raise self.retry(exc=e, countdown=5)
    else:
        print(f"Put request was successful! Task result: {result}")
        return result


@shared_task(bind=True)
def check_result_status(self, result, edited_field, submitted_value):
    # If the result contains a "code" field, it failed.
    # But this should never happen, as long as our validation is done correctly.
    if "code" in result:
        if result["code"] == 4004:
            message = "404 error received; No such tool found in Toolhub's records."
            print(message)
            return message
        elif result["code"] == "1000":
            # Yes, this response code is actually a string.  I am compiling a list for Bryan.
            res_message = result["errors"][0]["message"]
            message = f"Validation failure. Submitted {submitted_value} for {edited_field}, received following error: {res_message}"
            print(message)
            return message
    else:
        return "Status check passed"


@shared_task(bind=True)
def update_db(self, result, task_id, username):
    if result == "Status check passed":
        task = Task.query.get(task_id)
        task.user = username
        task.timestamp = datetime.datetime.now(datetime.timezone.utc)
        db.session.add(task)
        try:
            db.session.commit()
            print(f"{task.field_name} successfully updated for {task.tool_name}.")
            return
        except exc.DBAPIError as err:
            print(err)
            raise self.retry(exc=err, countdown=5)
    else:
        print(result)
        return
