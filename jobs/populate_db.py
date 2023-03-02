import json

from sqlalchemy import insert, select, text

from api import db
from api.models import Field, Task, Tool
from app import app

BASE_DIR = app.config["BASE_DIR"]
TOOLHUB_API_ENDPOINT = app.config["TOOLHUB_API_ENDPOINT"]


def insert_fields():
    """Insert data about annotations fields into the DB"""
    with open(f"{BASE_DIR}/tests/fixtures/fields.json") as fields:
        field_data = json.load(fields)
        db.session.bulk_insert_mappings(Field, field_data)
        db.session.commit()


def populate_db(data_set):
    """Accepts a list of dicts and runs each dict through the insertion process"""
    for tool in data_set:
        check_for_entry(tool)
    return "All done."


def check_for_entry(tool):
    """Receives a dict containing tool information and checks to see if it exists in the DB"""
    tool_name = tool["name"]
    result = db.session.execute(select(Tool).where(Tool.name == tool_name)).all()
    # If an entry exists move on to the deprecation check
    if len(result) > 0:
        print(f"{tool_name} already exists in database")
    else:
        add_tool_entry(tool)
    check_deprecation(tool)


def add_tool_entry(tool):
    """Receives a dict containing tool information and adds an entry to the tool table"""
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
    """Receives a dict containing tool information and checks its deprecation status."""
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
    """Receives a tool dict and checks/sorts the values of the core/annotations fields"""
    completed_fields = []
    empty_fields = []
    tool_name = tool["name"]
    for field in tool["annotations"]:
        # For each field in the annotations list:
        # There are a number of fields that we're not interested in working with right now.
        # In the future, some of them may be implemented.
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
        # A piece of information is missing only if it is absent in both the Core and Annotations layers
        # In order to be present, it only needs to appear in one or the other location
        # Therefore I need to check both sources.  First, does it exist in the Core?
        elif field in tool:
            # if it does, and it has neither a value there nor in the Annotations, add it to empty_fields
            if (tool[field] == [] or tool[field] is None) and (
                tool["annotations"][field] == [] or tool["annotations"][field] is None
            ):
                empty_fields.append(field)
            # if it exists and has a value, add to completed_fields and move on to the next field
            elif tool[field] != [] or tool[field] is not None:
                completed_fields.append(field)
                continue
        # In the event that the field doesn't exist in the Core, and if it has no value in Annotations, add to empty_fields
        elif tool["annotations"][field] == [] or tool["annotations"][field] is None:
            empty_fields.append(field)
        # And if it does have a value, add to completed_fields
        elif tool["annotations"][field] != [] or tool["annotations"][field] is not None:
            completed_fields.append(field)
    print({"Empty": empty_fields, "Completed": completed_fields})
    add_tasks(empty_fields, tool_name)
    remove_tasks(completed_fields, tool_name)


def remove_tasks(fields, tool_name):
    """Receives a list of fields and a tool name and removes matching, incomplete tasks from the task table"""
    for field in fields:
        # We're removing only incomplete tasks
        query = text(
            "DELETE FROM task WHERE field_name = :field_name AND tool_name = :tool AND user IS NULL"
        ).bindparams(field_name=field, tool=tool_name)
        db.session.execute(query)
        db.session.commit()
        # The following print statement was firing whether a tool was deleted or not.
        # It's nice that I can attempt to delete non-existent tasks without causing an error.
        # Is it worth throwing in another check to see if a task exists and then deleting it?
        # Then I could report what I was doing with more confidence.
        # print(f"Removed {field} task associated with {tool_name}.")
    # might be possible to do a bulk delete this way:
    # db.session.execute(delete(Task).where(and_(Task.field_name.in_(fields), Task.tool_name == tool_name, Task.user.is_(None))


def add_tasks(fields, tool_name):
    """Receives a list of fields and a tool name and adds tasks to the task table where none exist"""
    for field in fields:
        query = text(
            "SELECT * FROM task WHERE field_name = :field_name AND tool_name = :tool"
        ).bindparams(field_name=field, tool=tool_name)
        result = db.session.execute(query).all()
        # If we already have a task for that, we don't want to add a new one.
        if len(result) > 0:
            print(f"A task for {tool_name}, {field} already exists in the database")
            continue
        # But if we don't, we do
        # Right now this is just doing it one by one
        # A bulk insert would be more efficient, but I'll worry about that later
        else:
            task = {"tool_name": tool_name, "field_name": field}
            db.session.execute(insert(Task), task)
            db.session.commit()
            print(f"Added {field} task for {tool_name}")
