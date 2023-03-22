import datetime
import json

import flask
import requests
from flask_smorest import abort

from api import oauth


def build_put_request(form_data):
    """Take form data and return a dict to PUT to Toolhub"""
    multi_fields = ["audiences", "content_types", "tasks", "subject_domains"]
    field = form_data["field"]
    if field in multi_fields:
        value = form_data["value"].split(",")
    else:
        value = form_data["value"]
    comment = f"Updated {field} using Toolhunt"
    submission_data = {}
    submission_data[field] = value
    submission_data["comment"] = comment
    return submission_data


def get_current_user():
    """Get the username of currently logged-in user."""

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


class ToolhubClient:
    def __init__(self, endpoint):
        self.headers = {
            "User-Agent": "Toolhunt API",
            "Content-Type": "application/json",
        }
        self.endpoint = endpoint

    def get(self, tool):
        """Get data on a single tool and return a list"""
        url = f"{self.endpoint}{tool}"
        tool_data = []
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            api_response = response.json()
            tool_data.append(api_response)
            return tool_data
        except requests.exceptions.RequestException as e:
            print(e)

    def get_all(self):
        """Get data on all Toolhub tools."""
        url = f"{self.endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            api_response = response.json()
            tool_data = api_response["results"]
            while api_response["next"]:
                api_response = requests.get(
                    api_response["next"], headers=self.headers
                ).json()
                tool_data.extend(api_response["results"])
            return tool_data
        except requests.exceptions.RequestException as e:
            print(e)

    def get_count(self):
        """Get number of tools on Toolhub."""
        url = f"{self.endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            api_response = response.json()
            count = api_response["count"]
            return count
        except requests.exceptions.RequestException as e:
            print(e)

    def put(self, tool, data, token):
        """Take request data from the frontend and make a PUT request to Toolhub.

        This is routed through Celery
        """
        url = f"{self.endpoint}{tool}/annotations/"
        headers = dict(self.headers)
        headers.update({"Authorization": f"Bearer {token}"})
        # Having to do a manual json.dumps() to ensure proper formatting
        response = requests.put(url, data=json.dumps(data), headers=headers)
        api_response = response.json()
        return api_response
