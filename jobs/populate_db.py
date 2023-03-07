from sqlalchemy import insert, select, text

from api import db
from api.models import Task, Tool
from api.utils import ToolhubClient
from app import app

TOOLHUB_API_ENDPOINT = app.config["TOOLHUB_API_ENDPOINT"]
toolhub_client = ToolhubClient(TOOLHUB_API_ENDPOINT)


def run_bulk_population_job():
    """Fetches all tools from Toolhub and passes them to the populate function."""
    print("Getting tools from Toolhub...")
    data_set = toolhub_client.get_all()
    if type(data_set) is list:
        print("Tools acquired.  Processing.")
        insert_into_db(data_set)
        # otherwise it's an error message and needs handling
    else:
        print(data_set)
        # through in a retry here


def insert_into_db(data_set):
    """
    Accepts a list of tools (dicts) and runs each through the insertion process.

    The insertion process works as follows:

        Stage 1: Run check_for_entry (does the tool have an entry in the database?)
            1a. If no entry exists, add_tool_entry

        Stage 2: Run check_deprecation (is the tool deprecated?)
            2a. If the tool is deprecated, run remove_tasks to remove incomplete
                tasks associated with that tool from the db and move on to the next tool.

        Stage 3: Run sort_fields (this sorts the annotations fields into two categories: fields that have entries, and fields that do not)
            3a. Pass the list of empty fields to add_fields
            3b. Pass the list of filled fields to remove_fields

        Stage 4: Add/remove tasks as necessary.
            4a. add_fields will check to see if a task exists and add one if needed
            4b. remove_fields will check to see if an incomplete task exists, and will remove it if it does
        At this point the process is complete and the next tool is passed to check_for_entry.
    """
    for tool in data_set:
        check_for_entry(tool)
    return "All tools have been processed."


def check_for_entry(tool):
    """Receives a tool and checks to see if an entry exists in the DB."""
    tool_name = tool["name"]
    result = db.session.execute(select(Tool).where(Tool.name == tool_name)).all()
    # If an entry exists move on to the deprecation check
    if len(result) > 0:
        print(f"{tool_name} already exists in database.")
    else:
        add_tool_entry(tool)
    check_deprecation(tool)


def add_tool_entry(tool):
    """Receives a tool and adds an entry to the tool table."""
    tool = {
        "name": tool["name"],
        "title": tool["title"],
        "description": tool["description"],
        "url": tool["url"],
    }
    db.session.execute(insert(Tool), tool)
    db.session.commit()
    print(f"{tool['name']} inserted into db")


def check_deprecation(tool):
    """Receives a tool and checks its deprecation status."""
    tool_name = tool["name"]
    if tool["deprecated"] is True or tool["annotations"]["deprecated"] is True:
        print(f"{tool_name} is deprecated")
        fields = []
        # If a tool is deprecated, we want to remove the unfinished tasks associated with it.
        for field in tool["annotations"]:
            fields.append(field)
            remove_tasks(fields, tool_name)
    else:
        print(f"{tool_name} is not deprecated.  Sorting annotations fields.")
        sort_fields(tool)


def sort_fields(tool):
    """
    Receives a tool and checks/sorts the core/annotations fields.

    The process for field checking/sorting works as follows:

        For each field:

        Step 1: Check to see if the field is among fields_to_skip.
            There are several annotations fields that we're not working with right now.  In the future they may be implemented; for now the sorting function is instructed to ignore them.
            If so, move to the next field.

        Step 2: Check to see if the field exists in the Core layer.
            If it exists, and does not have a value there or in the Annotations layer, add it to the empty_fields list and move to the next field.
            If it exists, and has a value, add it to completed_fields and move to the next field.

        Step 3: Check for a value in the Annotations layer.
            If there is a value, add the field to completed_fields.
            If there is no value, add the field to empty_fields.

        When all the fields have been processed, pass empty_fields to add_tasks and completed_fields to remove_tasks.
    """
    completed_fields = []
    empty_fields = []
    tool_name = tool["name"]
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
                empty_fields.append(field)
                continue
            elif tool[field] != [] or tool[field] is not None:
                completed_fields.append(field)
                continue
        elif tool["annotations"][field] == [] or tool["annotations"][field] is None:
            empty_fields.append(field)
        elif tool["annotations"][field] != [] or tool["annotations"][field] is not None:
            completed_fields.append(field)
    print({"Empty": empty_fields, "Completed": completed_fields})
    add_tasks(empty_fields, tool_name)
    remove_tasks(completed_fields, tool_name)


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
            print(f"A task for {tool_name}, {field} already exists in the database")
            continue
        else:
            task = {"tool_name": tool_name, "field_name": field}
            db.session.execute(insert(Task), task)
            db.session.commit()
            print(f"Added {field} task for {tool_name}")
