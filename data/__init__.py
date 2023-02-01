from data.toolData import toolData
from data.fieldData import fieldData
from data.taskData import taskData
from api.models import Tool, Field, Task
from api.resources.db import db

def insertData():
  db.engine.execute(Tool.__table__.insert(), toolData)
  db.engine.execute(Field.__table__.insert(), fieldData)
  db.engine.execute(Task.__table__.insert(), taskData)