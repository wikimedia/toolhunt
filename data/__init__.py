from data.toolData import toolData
from data.fieldData import fieldData
from data.taskData import taskData
from api.models import Tool, Field, Task
from api.resources.db import db

def insertData():
  db.session.bulk_insert_mappings(Tool, toolData)
  db.session.bulk_insert_mappings(Field, fieldData)
  db.session.bulk_insert_mappings(Task, taskData)
  db.session.commit()