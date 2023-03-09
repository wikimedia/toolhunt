import logging

from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert

from api import db
from api.models import Task, Tool
from api.utils import ToolhubClient
from app import app

logging.basicConfig(
    filename="populate_db.log",
    format="%(asctime)s:%(levelname)s:%(message)s",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger()

TOOLHUB_API_ENDPOINT = app.config["TOOLHUB_API_ENDPOINT"]
toolhub_client = ToolhubClient(TOOLHUB_API_ENDPOINT)


def run_bulk_population_job():
    """Fetches all tools from Toolhub and passes them to the populate function."""
    logger.info("Getting tools from Toolhub.")
    data_set = toolhub_client.get_all()
    if type(data_set) is list:
        logger.info("Tools acquired from Toolhub.")
        insert_into_db(data_set)
        # otherwise it's an error message and needs handling
    else:
        logger.error(data_set)
        # throw in a retry here??


def insert_into_db(data_set):
    """
    Accepts a list of tools (dicts) and runs each through the insertion process.

    The insertion process works as follows:

        Stage 1: Run add_or_update_tool (as the name suggests, this will upsert a tool entry) and check to see if the tool is deprecated
            1a. If the tool is deprecated, remove incomplete tasks associated with that tool from the db and move on to the next tool.

        Stage 2: Run sort_fields (this sorts the annotations fields into two categories: fields that have entries, and fields that do not)
            2a. Pass the list of empty fields to add_fields
            2b. Pass the list of filled fields to remove_fields

        Stage 3: Add/remove tasks as necessary.
            3a. add_fields will check to see if a task exists and add one if needed
            3b. remove_fields will check to see if an incomplete task exists, and will remove it if it does

        At this point the process is complete and the next tool is passed to add_or_update_tool.
    """
    logger.info("Begin tool processing and db insertion.")
    for tool in data_set:
        tool_name = tool["name"]
        add_or_update_tool(tool)
        if is_deprecated(tool):
            all_fields = compile_field_list(tool)
            remove_tasks(all_fields, tool_name)
            logger.info(f"{tool_name} deprecated.")
            continue
        field_dict = sort_fields(tool)
        remove_tasks(field_dict["complete"], tool_name)
        add_tasks(field_dict["empty"], tool_name)
        logger.info(f"{tool_name} processed.")
    logger.info("Tool processing complete.")
    return


def add_or_update_tool(tool):
    """Receives a tool and adds an entry to the tool table."""
    insert_stmt = insert(Tool).values(
        name=tool["name"],
        title=tool["title"],
        description=tool["description"],
        url=tool["url"],
    )
    on_duplicate_insert_stmt = insert_stmt.on_duplicate_key_update(
        title=tool["title"], description=tool["description"], url=tool["url"]
    )
    db.session.execute(on_duplicate_insert_stmt)
    db.session.commit()


def is_deprecated(tool):
    """Returns a Boolean indicating if the tool is deprecated."""
    return tool["deprecated"] or tool["annotations"]["deprecated"]


def compile_field_list(tool):
    """Returns a list of all annotations fields."""
    fields = []
    for field in tool["annotations"]:
        fields.append(field)
        return fields


def sort_fields(tool):
    """
    Receives a tool and checks/sorts the core/annotations fields.

    The process for field checking/sorting works as follows:

        For each field:

        Step 1: Check to see if the field is among fields_to_skip.
            There are several annotations fields that we're not working with right now.  In the future they may be implemented; for now the sorting function is instructed to ignore them.
            If so, move to the next field.

        Step 2: Check to see if the field exists in the Core layer.
            If it exists, and does not have a value there or in the Annotations layer, add it to field_list["empty"] and move to the next field.
            If it exists, and has a value, add it to field_list["complete"] and move to the next field.

        Step 3: Check for a value in the Annotations layer.
            If there is a value, add the field to field_list["complete"].
            If there is no value, add the field to field_list["empty"].

        When all the fields have been processed, return the dict to the main function.
    """
    field_dict = {"complete": [], "empty": []}
    for field in tool["annotations"]:
        fields_to_skip = [
            "replaced_by",
            "deprecated",
            "experimental",
            "developer_docs_url",
            "user_docs_url",
            "feedback_url",
            "privacy_policy_url",
            "for_wikis",
            "available_ui_languages",
        ]
        if field in fields_to_skip:
            continue
        elif field in tool:
            if (tool[field] == [] or tool[field] is None) and (
                tool["annotations"][field] == [] or tool["annotations"][field] is None
            ):
                field_dict["empty"].append(field)
                continue
            elif tool[field] != [] or tool[field] is not None:
                field_dict["complete"].append(field)
                continue
        elif tool["annotations"][field] == [] or tool["annotations"][field] is None:
            field_dict["empty"].append(field)
        elif tool["annotations"][field] != [] or tool["annotations"][field] is not None:
            field_dict["complete"].append(field)
    return field_dict


def remove_tasks(fields, tool_name):
    """
    Receives fields and a tool name and removes incomplete tasks.

    For each field in the list, the function removes a matching, INCOMPLETE (i.e., one with no value for "user") task from the db, if one exists.
    """
    for field in fields:
        query = text(
            "DELETE FROM task WHERE field_name = :field_name AND tool_name = :tool AND user IS NULL"
        ).bindparams(field_name=field, tool=tool_name)
        db.session.execute(query)
        db.session.commit()


def add_tasks(fields, tool_name):
    """
    Receives fields and a tool name and adds tasks.

    For each field in the list, the function checks to see if a task exists for that particular tool and field type.  If none exists, it adds one.
    """
    for field in fields:
        query = text(
            "SELECT * FROM task WHERE field_name = :field_name AND tool_name = :tool"
        ).bindparams(field_name=field, tool=tool_name)
        result = db.session.execute(query).all()
        if len(result) > 0:
            continue
        else:
            task = {"tool_name": tool_name, "field_name": field}
            db.session.execute(insert(Task), task)
            db.session.commit()
