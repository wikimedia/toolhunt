from celery import shared_task

from api.utils import ToolhubClient


@shared_task
def make_put_request(name_string, data_obj, token):
    """Create a PUT task using Celery and ToolhubClient."""
    from app import app

    toolhub_client = ToolhubClient(app.config["TOOLHUB_API_ENDPOINT"])
    return toolhub_client.put(name_string, data_obj, token)
