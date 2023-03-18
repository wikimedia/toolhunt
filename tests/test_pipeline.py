import datetime

from api.logging import logger
from jobs.populate_db import clean_tool_data, update_task_table, update_tool_table


def run_test_pipeline(raw_data_set):
    try:
        # Transform
        logger.info("Cleaning tool data")
        tools_clean_data = clean_tool_data(raw_data_set)
        logger.info(f"Results of data cleaning: {tools_clean_data}.")
        logger.info("Updating tools...")
        # Load
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        update_tool_table(tools_clean_data, timestamp)
        logger.info("Tools updated.  Updating tasks.")
        update_task_table(tools_clean_data, timestamp)
    except Exception as err:
        logger.error(f"{err.args}")
