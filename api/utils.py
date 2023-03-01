import datetime

import flask
import requests
from flask_smorest import abort


def build_request(task_data):
    """Take data and return an object to PUT to Toolhub"""
    field = task_data["field"]
    value = task_data["value"]
    comment = f"Updated {field} using Toolhunt"
    data = {}
    data[field] = value
    data["comment"] = comment
    return data


def get_current_user():
    """Get the username of currently logged-in user."""
    # This import is still throwing an error for me when I put it at the top of the file
    from app import oauth  # noqa

    if not flask.session:
        abort(401, message="No user is currently logged in.")
    else:
        try:
            resp = oauth.toolhub.get("user/", token=flask.session["token"])
            resp.raise_for_status()
            profile = resp.json()
            username = profile["username"]
            return username
        except requests.exceptions.HTTPError as err:
            print(err)
            abort(401, message="User authorization failed.")
        except requests.exceptions.ConnectionError as err:
            print(err)
            abort(503, message="Server connection failed.  Please try again.")
        except requests.exceptions.RequestException as err:
            print(err)
            abort(501, message="Server encountered an unexpected error.")


def generate_past_date(days):
    """Take an integer X and return a datetime object X days in the past."""
    today = datetime.datetime.now(datetime.timezone.utc)
    past_date = today - datetime.timedelta(days=days)
    return past_date


# leaving this here for reference/historical reasons
# the same is found in __init__.py
# I had initially split it here and created a
# tasks.py file to hold the tasks.
# Ultimately that failed due to circular import issues.
# I'll try it again later.

# def make_celery(app):
#     celery = current_celery_app
#     # This may be what was causing a problem with the env variable configuration.
#     # Bear this in mind if I try to update the env var names in future.
#     celery.config_from_object(app.config, namespace="CELERY")
#     return celery


class ToolhubClient:
    def __init__(self, endpoint):
        self.headers = {"User-Agent": "Toolhunt API"}
        self.endpoint = endpoint

    def get(self, tool):
        """Get data on a single tool and return a list"""
        url = f"{self.endpoint}{tool}"
        tool_data = []
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP error - most likely no tool by that name exists")
            print(e.args[0])
        except requests.exceptions.ConnectionError:
            print("Connection error.  Please try again.")
        except requests.exceptions.Timeout:
            print("Request timed out.")
            # Could automatically retry
        except requests.exceptions.RequestException as e:
            print("Something went wrong.")
            print(e)
        api_response = response.json()
        tool_data.append(api_response)
        return tool_data

    def get_all(self):
        """Get data on all Toolhub tools."""
        url = f"{self.endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP error")
            print(e.args[0])
        except requests.exceptions.ConnectionError:
            print("Connection error.  Please try again.")
        except requests.exceptions.Timeout:
            print("Request timed out.")
            # Could automatically retry
        except requests.exceptions.RequestException as e:
            print("Something went wrong.")
            print(e)
        api_response = response.json()
        tool_data = api_response["results"]
        while api_response["next"]:
            api_response = requests.get(
                api_response["next"], headers=self.headers
            ).json()
            tool_data.extend(api_response["results"])
        return tool_data

    def put(self, tool, data):
        """Take request data from the frontend and make a PUT request to Toolhub."""
        url = f"{self.endpoint}{tool}/annotations/"
        headers = dict(self.headers)
        headers.update(
            {"Authorization": f'Bearer {flask.session["token"]["access_token"]}'}
        )        
        response = requests.put(url, data=data, headers=headers)
        r = response.status_code
        return r
    

    def put_celery(self, tool, data, token):
        """Take request data from the frontend and make a PUT request to Toolhub.
        
        This is routed through Celery
        Currently a WIP
        """
        url = f"{self.endpoint}{tool}/annotations/"
        headers = dict(self.headers)
        headers.update({"Authorization": f"Bearer {token}"})
        response = requests.put(url, data=data, headers=headers)
        r = response.status_code
        return r