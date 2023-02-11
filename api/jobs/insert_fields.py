from api import db
from api.tests.fixtures.data import field_data
from api.models import Field

def insert_fields():
  db.session.bulk_insert_mappings(Field, field_data)