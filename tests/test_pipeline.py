import datetime

from jobs.populate_db import clean_tool_data, update_task_table, update_tool_table


def run_test_pipeline(raw_data_set) -> None:
    # Transform
    tools_clean_data = clean_tool_data(raw_data_set)
    # Load
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    update_tool_table(tools_clean_data, timestamp)
    update_task_table(tools_clean_data)
