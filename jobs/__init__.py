from jobs.get_tools import get_tools, get_single_tool
from jobs.insert_tools import *
from jobs.insert_fields import insert_fields

def populate_db():
  tools = get_tools()
  for tool in tools:
    check_for_entry(tool)
  return "All done."