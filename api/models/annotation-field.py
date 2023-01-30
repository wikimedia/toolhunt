from api.resources.db import db

class AnnotationField(db.Model):
  __tablename__ = "annotation_field"

  name = db.Column(db.String(80), primary_key=True, nullable=False)
  description = db.Column(db.String(2047), nullable=False)
  # input_type = db.Column(db.String(24), nullable=False)
  # options = db.Column(db.Enum, nullable=True)
  # constraints = db.Column(db.String, nullable=True)
  # pattern = db.Column(db.String, nullable=True)