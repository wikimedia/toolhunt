from marshmallow import Schema, fields

class FieldSchema(Schema):
  name = fields.Str(required=True)
  description = fields.Str(required=True)
  input_options = fields.Dict(required=False)
  pattern = fields.Str(required=False)

class ToolSchema(Schema):
  name = fields.Str(required=True)
  title = fields.Str(required=True)
  description = fields.Str(required=True)
  url = fields.Str(required=True)

class TaskSchema(Schema):
  id = fields.Int(dump_only=True)
  tool_name = fields.Str(required=True, load_only=True)
  tool = fields.Nested(ToolSchema(), dump_only=True)
  field_name = fields.Str(required=True, load_only=True)
  field = fields.Nested(FieldSchema(), dump_only=True)
  user = fields.Str(required=False)
  timestamp = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z', required=False)

class TaskCompleteSchema(Schema):
  tool = fields.Str(required=True)
  field = fields.Str(required=True)
  value = fields.Str(required=True)

class ContributionSchema(Schema):
  user = fields.Str(required=True)
  timestamp = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z', required=True)
  tool = fields.Nested(ToolSchema())
  field_name = fields.Str(required=True)

class ContributionLimitSchema(Schema):
  limit = fields.Int(required=False)

class ScoreSchema(Schema):
  user = fields.Str(required=True)
  score = fields.Int(required=True)

class ScoreLimitSchema(Schema):
  since = fields.Int(required=False)