import datetime
from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, text
from sqlalchemy.dialects.mysql import insert

from api import db
from api.models import Task, Tool
from api.utils import ToolhubClient
from app import app

TOOLHUB_API_ENDPOINT = app.config["TOOLHUB_API_ENDPOINT"]
toolhub_client = ToolhubClient(TOOLHUB_API_ENDPOINT)

# Transform

# Parameters
ANNOTATIONS = {
    "audiences",
    "content_types",
    "tasks",
    "subject_domains",
    "wikidata_qid",
    "icon",
    "tool_type",
    "repository",
    "api_url",
    "translate_url",
    "bugtracker_url",
}


# Functions
@dataclass
class ToolhuntTool:
    name: str
    title: str
    description: str
    url: str
    missing_annotations: set[str]
    deprecated: bool

    @property
    def is_completed(self):
        return len(self.missing_annotations) == 0


def is_deprecated(tool: dict[str, Any]):
    return tool["deprecated"] or tool["annotations"]["deprecated"]


def get_missing_annotations(
    tool_info: dict[str, Any], filter_by: set[str] = ANNOTATIONS
):
    missing = set()

    for k, v in tool_info["annotations"].items():
        value = v or tool_info.get(k, v)
        if value in (None, [], "") and k in filter_by:
            missing.add(k)

    return missing


def clean_tool_data(tool_data: list[dict[str, any]]):
    tools = []
    for tool in tool_data:
        t = ToolhuntTool(
            name=tool["name"],
            title=tool["title"],
            description=tool["description"],
            url=tool["url"],
            missing_annotations=get_missing_annotations(tool),
            deprecated=is_deprecated(tool),
        )
        if not t.deprecated and not t.is_completed:
            tools.append(t)
    return tools


# Load


def upsert_tool(tool: ToolhuntTool, timestamp):
    """Inserts a tool in the Tool table if it doesn't exist, and updates it if it does."""

    insert_stmt = insert(Tool).values(
        name=tool.name,
        title=tool.title,
        description=tool.description,
        url=tool.url,
        last_updated=timestamp,
    )
    on_duplicate_insert_stmt = insert_stmt.on_duplicate_key_update(
        title=tool.title,
        description=tool.description,
        url=tool.url,
        last_updated=timestamp,
    )
    db.session.execute(on_duplicate_insert_stmt)
    db.session.commit()


def remove_stale_tools(expiration_days: int = 1):
    """Removes expired tools from the Tool table."""
    limit = datetime.datetime.now() - datetime.timedelta(days=expiration_days)
    delete_stmt = delete(Tool).where(Tool.last_updated < limit)
    db.session.execute(delete_stmt)
    db.session.commit()


def update_tool_table(tools: list[ToolhuntTool], timestamp, **kwargs):
    """Upserts tool records and removes stale tools"""

    [upsert_tool(tool, timestamp) for tool in tools]

    remove_stale_tools()


def insert_task(tool_name: str, field: str):
    """Inserts a tool in the Tool table if it doesn't exist."""
    query = text(
        "SELECT * FROM task WHERE field_name = :field AND tool_name = :tool_name"
    ).bindparams(field=field, tool_name=tool_name)
    result = db.session.execute(query).all()
    if not result:
        insert_stmt = insert(Task).values(
            tool_name=tool_name,
            field_name=field,
        )
        db.session.execute(insert_stmt)
        db.session.commit()


def update_task_table(tools: list[ToolhuntTool]):
    """Inserts task records"""

    for tool in tools:
        for field in tool.missing_annotations:
            insert_task(tool.name, field)


# Pipeline


def run_pipeline(**kwargs):
    # Extract
    tools_raw_data = toolhub_client.get_all()
    # Transform
    tools_clean_data = clean_tool_data(tools_raw_data)
    # Load
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    update_tool_table(tools_clean_data, timestamp)
    update_task_table(tools_clean_data)


# This will populate the db if empty, or update all tool and task records if not.
# run_pipeline()
