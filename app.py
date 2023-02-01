from api import create_app
from data import insertData

app = create_app()

@app.route('/')
def runInsertion():
  insertData()
  return "Data inserted!"

