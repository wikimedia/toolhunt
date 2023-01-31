from marshmallow import Schema, fields

class UserSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)

class FieldSchema(Schema):
  name = fields.Str(required=True)
  description = fields.Str(required=True)

class ToolSchema(Schema):
  name = fields.Str(required=True)
  title = fields.Str(required=True)
  description = fields.Str(required=True)
  url = fields.Str(required=True)
  # repository = fields.Str(required=False)

class TaskSchema(Schema):
  id = fields.Int(dump_only=True)
  tool_name = fields.Str(required=True)
  tool = fields.Nested(ToolSchema(), dump_only=True)
  field_name = fields.Str(required=True)
  field = fields.Nested(FieldSchema(), dump_only=True)
  user = fields.Str(required=False)
  # date
