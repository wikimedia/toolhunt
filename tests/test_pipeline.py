import datetime
import logging

from jobs.populate_db import clean_tool_data, update_task_table, update_tool_table

logging.basicConfig(
    filename="test_pipeline.log",
    format="%(asctime)s:%(levelname)s:%(message)s",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger()


def run_test_pipeline(raw_data_set):
    # Transform
    logger.info("Cleaning tool data")
    tools_clean_data = clean_tool_data(raw_data_set)
    logger.info(f"Results: {tools_clean_data}")
    logger.info("Moving to tool update")
    # Load
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    update_tool_table(tools_clean_data, timestamp)
    logger.info("Tools updated")
    logger.info("Updating tasks")
    update_task_table(tools_clean_data, timestamp)
