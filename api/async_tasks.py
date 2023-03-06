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


@shared_task()
def process_result(result, task_id, edited_field, submitted_value, username):
    # If the result contains a "code" field, it failed.
    # But this should never happen, as long as our validation is done correctly.
    if "code" in result:
        if result["code"] == 4004:
            print("404 error received; No such tool found in Toolhub's records.")
            return
        elif result["code"] == "1000":
            # Yes, this response code is actually a string.  I am compiling a list for Bryan.
            res_message = result["errors"][0]["message"]
            print(
                f"Validation failure. Submitted {submitted_value} for {edited_field}, received following error: {res_message}"
            )
    else:
        # The alternative to an error message is a dict containing the annotations fields for the tool.
        # We check to make sure that the value we submitted matches the returned value.
        if result[edited_field] == submitted_value:
            # If so, we update our database
            task = Task.query.get(task_id)
            tool_name = task.tool_name
            task.user = username
            task.timestamp = datetime.datetime.now(datetime.timezone.utc)
            db.session.add(task)
            try:
                db.session.commit()
                print(f"{edited_field} successfully updated for {tool_name}.")
                return
            except exc.DBAPIError as err:
                print(err)
                # I'd need to sort out a retry here, too
                return
        else:
            # Another job for logging here.  We'd reach this point if the annotations
            # data returned from Toolhub does not contain the information we just sent.
            # I have no idea what set of circumstances could lead to this.
            print("Something went wrong with inserting the data into Toolhub")
            return
