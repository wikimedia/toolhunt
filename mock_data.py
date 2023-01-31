from api.resources.db import db
from api.models import Tool, Field, Task

fieldData = [
  {
    "name": "wikidata_qid", 
    "description": "a thing for doing the thing"
  },
  {
    "name": "tool_type", 
    "description": "this other thing"
  }
]

toolData = [
  {
    "title": "Wikidata Todo",
    "name": "mm_wikidata_todo",
    "description": "Shows you little things you can do on Wikidata.",
    "url": "http://tools.wmflabs.org/wikidata-todo"
  },
  {
    "title": "A totally fake tool",
    "name": "totally_fake",
    "description": "I just made this one up to test some things.",
    "url": "http://www.google.com"
  },
  {
    "title": "Pywikibot",
    "name": "pywikibot",
    "description":
      "Python library and collection of scripts that automate work on MediaWiki sites",
    "url": "https://www.mediawiki.org/wiki/Special:MyLanguage/Manual:Pywikibot"
  }
]

taskData = [
  {
    "tool_name": "pywikibot",
    "field_name": "tool_type"
  },
   {
    "tool_name": "totally_fake",
    "field_name": "wikidata_qid"
  },
  {
    "tool_name": "mm_wikidata_todo",
    "field_name": "wikidata_qid"
  }
]

def insertData():
  db.engine.execute(Tool.__table__.insert(), toolData)
  db.engine.execute(Field.__table__.insert(), fieldData)
  db.engine.execute(Task.__table__.insert(), taskData)