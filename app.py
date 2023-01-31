from api import create_app
from mock_data import insertData

app = create_app()

@app.route('/')
def runInsertion():
  insertData()
  return "Data inserted!"

