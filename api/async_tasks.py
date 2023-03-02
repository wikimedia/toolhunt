import datetime
from celery import shared_task
from flask import current_app
from api import db
from api.utils import ToolhubClient, get_current_user
from flask_smorest import abort
from sqlalchemy import exc


@shared_task(bind=True)
def make_put_request(self, task_obj, tool_name, data_obj, token):
    """Create a PUT task using Celery and ToolhubClient."""
    for key in data_obj:
        if key is not "comment":
            field_name = key
            print(f'{data_obj[field_name]} as value for {field_name}')
    toolhub_client = ToolhubClient(current_app.config["TOOLHUB_API_ENDPOINT"])
    try:
        put_task = toolhub_client.put(tool_name, data_obj, token)
    except Exception as e:
        print(f'Exception {e} raised, retrying after 5 seconds...')
        raise self.retry(exc=e, countdown=5)
    else:
        response = put_task.get()
        # If the response contains a "code" field, it failed.
        # But this should never happen, as long as our validation is done correctly.
        if "code" in response:
            if response["code"] == 4004:
                print("404 error received; No such tool found in Toolhub's records.")
                return
            elif response["code"] == "1000":
                # Yes, this response code is actually a string.  I am compiling a list for Bryan.
                res_message = response["errors"][0]["message"]
                for key in data_obj:
                    if key is not "comment":
                        field_name = key
                print(f'Validation failure. Submitted {data_obj[field_name]} as value for {field_name}, received following error: {res_message}')
        else:
            # The alternative to an error message is a dict containing the annotations fields for the tool.
            # We check to make sure that the value we submitted matches the returned value.
            edited_field = task_obj["field"]
            expected_value = task_obj["value"]
            if response[edited_field] == expected_value:
                # If so, we update our database
                username = get_current_user()
                task_obj.user = username
                task_obj.timestamp = datetime.datetime.now(datetime.timezone.utc)
                db.session.add(task_obj)
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
                        