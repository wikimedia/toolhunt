import datetime

from celery import shared_task
from flask import current_app
from sqlalchemy import exc

from api import db
from api.models import CompletedTask, Task
from api.utils import ToolhubClient


@shared_task(bind=True, name="toolhunt-api.tasks.make_put_request")
def make_put_request(self, tool_name, submission_data, token):
    """Create a PUT task using Celery and ToolhubClient."""
    toolhub_client = ToolhubClient(current_app.config["TOOLHUB_API_ENDPOINT"])
    try:
        result = toolhub_client.put(tool_name, submission_data, token)
    except Exception as e:
        print(f"Exception {e} raised, retrying after 5 seconds...")
        raise self.retry(exc=e, countdown=5)
    else:
        return f"PUT request made.  Response from Toolhub: {result}"


@shared_task(bind=True, name="toolhunt-api.tasks.check_result_status")
def check_result_status(self, result, edited_field, submitted_value):
    # If the result contains a "code" field, it failed.
    # But this should never happen, as long as our validation is done correctly.
    if "code" in result:
        if result["code"] == 4004:
            message = "404 error received; No such tool found in Toolhub's records."
            return message
        elif result["code"] == "1000":
            res_message = result["errors"][0]["message"]
            message = f"Validation failure. Submitted {submitted_value} for {edited_field}, received following error: {res_message}"
            return message
    else:
        return "Status check passed; Toolhub records updated successfully."


@shared_task(bind=True, name="toolhunt-api.tasks.update_db")
def update_db(self, result, task_id, form_data, tool_title):
    if result == "Status check passed; Toolhub records updated successfully.":
        task = Task.query.get(task_id)
        completedTask = CompletedTask(
            tool_name=form_data["tool"],
            tool_title=tool_title,
            field=form_data["field"],
            user=form_data["user"],
            completed_date=datetime.datetime.now(datetime.timezone.utc),
        )
        try:
            db.session.add(completedTask)
            db.session.delete(task)
            db.session.commit()
            return "Toolhunt database successfully updated."
        except (exc.DBAPIError, exc.SQLAlchemyError) as err:
            print(err)
            raise self.retry(exc=err, countdown=10)
    else:
        return f"Submission failure.  Reason: {result}"
