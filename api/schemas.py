import json

from marshmallow import Schema, fields, pre_dump


class FieldSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    input_options = fields.Dict(required=False)
    pattern = fields.Str(required=False)

    @pre_dump
    def serialize_input_options(self, data, **kwargs):
        """Convert input_options from bytes obj to dict."""
        try:
            if data.input_options and not isinstance(data.input_options, dict):
                input_options = data.input_options.decode().replace("'", '"')
                data.input_options = json.loads(input_options)
                return data
        except Exception as e:
            print(f"An error occurred: {e}")

        return data


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


class PutRequestSchema(Schema):
    tool = fields.Str(required=True)
    field = fields.Str(required=True)
    value = fields.Str(required=True)
    user = fields.Str(required=True)


class ContributionSchema(Schema):
    user = fields.Str(required=True)
    completed_date = fields.DateTime(format="%Y-%m-%dT%H:%M:%S%z", required=True)
    tool_name = fields.Str(required=True)
    tool_title = fields.Str(required=True)
    field = fields.Str(required=True)


class ContributionLimitSchema(Schema):
    limit = fields.Int(required=False)


class ScoreSchema(Schema):
    user = fields.Str(required=True)
    score = fields.Int(required=True)


class ScoreLimitSchema(Schema):
    since = fields.Int(required=False)


class UserSchema(Schema):
    username = fields.Str(required=True)


class ContributionsMetricsSchema(Schema):
    Total_contributions = fields.Int(required=True)
    Global_contributions_from_the_last_30_days = fields.Int(required=True)


class TasksMetricsSchema(Schema):
    Number_of_tasks_in_the_Toolhunt_database = fields.Int(required=True)
    Number_of_unfinished_tasks_in_the_Toolhunt_database = fields.Int(required=True)


class ToolsMetricsSchema(Schema):
    Number_of_tools_on_record = fields.Int(required=True)
    Number_of_tools_with_incomplete_information = fields.Int(required=True)


class UserMetricsSchema(Schema):
    My_total_contributions = fields.Int(required=True)
    My_contributions_in_the_past_30_days = fields.Int(required=True)
