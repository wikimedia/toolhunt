import flask
from celery import chain
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import desc, exc, func, text

from api import db
from api.async_tasks import check_result_status, make_put_request, update_db
from api.models import CompletedTask, Field, Task, Tool
from api.schemas import (
    ContributionLimitSchema,
    ContributionSchema,
    ContributionsMetricsSchema,
    FieldSchema,
    PutRequestSchema,
    ScoreLimitSchema,
    ScoreSchema,
    TaskSchema,
    TasksMetricsSchema,
    ToolsMetricsSchema,
    UserMetricsSchema,
    UserSchema,
)
from api.utils import (
    ToolhubClient,
    build_put_request,
    generate_past_date,
    get_current_user,
)

toolhub_client = ToolhubClient(current_app.config["TOOLHUB_API_ENDPOINT"])

contributions = Blueprint(
    "contributions",
    __name__,
    description="Get information about contributions made using Toolhunt.",
)


@contributions.route("/api/contributions/")
class Contributions(MethodView):
    @contributions.arguments(ContributionLimitSchema, location="query", required=False)
    @contributions.response(200, ContributionSchema(many=True))
    def get(self, query_args):
        """List contributions made using Toolhunt."""
        if query_args:
            limit = query_args["limit"]
            return CompletedTask.query.order_by(
                desc(CompletedTask.completed_date)
            ).limit(int(limit))
        else:
            return CompletedTask.query.order_by(desc(CompletedTask.completed_date))


@contributions.route("/api/contributions/<string:user>")
class ContributionsByUser(MethodView):
    @contributions.response(200, ContributionSchema(many=True))
    def get(self, user):
        """List the ten most recent contributions by a user."""
        # Ideally in the future we could introduce pagination and return all of a user's contributions
        return (
            CompletedTask.query.filter(CompletedTask.user == user)
            .order_by(desc(CompletedTask.completed_date))
            .limit(10)
        )


@contributions.route("/api/contributions/top-scores")
class ContributionHighScores(MethodView):
    @contributions.arguments(ScoreLimitSchema, location="query", required=False)
    @contributions.response(200, ScoreSchema(many=True))
    def get(self, query_args):
        """List the most prolific Toolhunters, by number of contributions."""
        if query_args:
            end_date = generate_past_date(query_args["since"])
            scores_query = text(
                "SELECT DISTINCT user, COUNT(*) AS 'score' FROM completed_task WHERE completed_date >= :date GROUP BY user ORDER BY 2 DESC LIMIT 30"
            ).bindparams(date=end_date)
        else:
            scores_query = text(
                "SELECT DISTINCT user, COUNT(*) AS 'score' FROM completed_task GROUP BY user ORDER BY 2 DESC LIMIT 30"
            )
        results = db.session.execute(scores_query)
        scores = []
        for row in results:
            result = {"user": row[0], "score": row[1]}
            scores.append(result)
        return scores


fields = Blueprint(
    "fields", __name__, description="Get information about annotations fields."
)


@fields.route("/api/fields")
class FieldList(MethodView):
    @fields.response(200, FieldSchema(many=True))
    def get(self):
        """List all annotations fields."""
        return Field.query.all()


@fields.route("/api/fields/<string:name>")
class FieldInformation(MethodView):
    @fields.response(200, FieldSchema)
    def get(self, name):
        """Get information about an annotations field."""
        return Field.query.get_or_404(name)


metrics = Blueprint(
    "metrics",
    __name__,
    description="Get information about various metrics related to Toolhunt.",
)


@metrics.route("/api/metrics/contributions")
class ContributionsMetrics(MethodView):
    @metrics.response(200, ContributionsMetricsSchema)
    def get(self):
        """Get metrics pertaining to contributions."""
        try:
            results = {}
            date_limit = generate_past_date(30)
            total = db.session.execute(
                text("SELECT COUNT(*) FROM completed_task")
            ).all()
            results["Total_contributions"] = total[0][0]
            thirty_day = db.session.execute(
                text(
                    "SELECT COUNT(*) FROM completed_task WHERE completed_date >= :date"
                ).bindparams(date=date_limit)
            ).all()
            results["Global_contributions_from_the_last_30_days"] = thirty_day[0][0]
            return results
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


@metrics.route("/api/metrics/tasks")
class TaskMetrics(MethodView):
    @metrics.response(200, TasksMetricsSchema)
    def get(self):
        """Get metrics pertaining to Toolhunt tasks."""
        try:
            results = {}
            completed_tasks = db.session.execute(
                text("SELECT COUNT(*) FROM completed_task")
            ).all()
            incomplete_tasks = db.session.execute(
                text("SELECT COUNT(*) FROM task")
            ).all()
            results["Number_of_tasks_in_the_Toolhunt_database"] = (
                completed_tasks[0][0] + incomplete_tasks[0][0]
            )

            results[
                "Number_of_unfinished_tasks_in_the_Toolhunt_database"
            ] = incomplete_tasks[0][0]
            return results
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


@metrics.route("/api/metrics/tools")
class ToolMetrics(MethodView):
    @metrics.response(200, ToolsMetricsSchema)
    def get(self):
        """Get metrics pertaining to tools."""
        try:
            results = {}
            total = toolhub_client.get_count()
            results["Number_of_tools_on_record"] = total
            missing_info = db.session.execute(text("SELECT COUNT(*) FROM tool")).all()
            results["Number_of_tools_with_incomplete_information"] = missing_info[0][0]
            return results
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


@metrics.route("/api/metrics/user")
class UserMetrics(MethodView):
    @metrics.response(200, UserMetricsSchema)
    def get(self):
        """Get metrics pertaining to the currently logged-in user."""
        user = get_current_user()
        if type(user) == str:
            date_limit = generate_past_date(30)
            try:
                results = {}
                total_cont = db.session.execute(
                    text(
                        "SELECT COUNT(*) FROM completed_task WHERE user = :user"
                    ).bindparams(user=user)
                ).all()
                results["My_total_contributions"] = total_cont[0][0]
                thirty_cont = db.session.execute(
                    text(
                        "SELECT COUNT(*) FROM completed_task WHERE user = :user AND completed_date >= :date"
                    ).bindparams(user=user, date=date_limit)
                ).all()
                results["My_contributions_in_the_past_30_days"] = thirty_cont[0][0]
                return results
            except exc.OperationalError as err:
                print(err)
                abort(503, message="Database connection failed.  Please try again.")
        else:
            return user


tasks = Blueprint(
    "tasks", __name__, description="Get incomplete tasks and submit data to Toolhub."
)


@tasks.route("/api/tasks")
class TaskList(MethodView):
    @tasks.response(200, TaskSchema(many=True))
    def get(self):
        "Get ten incomplete tasks."
        return Task.query.order_by(func.random()).limit(10)


@tasks.route("/api/tasks/tool/<string:tool_name>")
class TaskByTool(MethodView):
    @tasks.response(200, TaskSchema(many=True))
    def get(self, tool_name):
        "Get a set of tasks for a given tool."
        try:
            # If tool_test fails then the tool name is bad and we can stop.
            tool_test = Tool.query.get_or_404(tool_name)
            if tool_test:
                tasks = Task.query.filter_by(tool_name=tool_name)
                return tasks
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


@tasks.route("/api/tasks/type/<string:task_type>")
class TaskByType(MethodView):
    @tasks.response(200, TaskSchema(many=True))
    def get(self, task_type):
        "Get a set of tasks of a selected type."
        # Could expand to select multiple task types
        try:
            tasks = Task.query.filter_by(field_name=task_type).limit(10)
            return tasks
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


@tasks.route("/api/tasks/<string:task_id>")
class TaskById(MethodView):
    @tasks.response(200, TaskSchema)
    def get(self, task_id):
        """Get information about a specific task."""
        task = Task.query.get_or_404(task_id)
        return task

    @tasks.arguments(PutRequestSchema)
    @tasks.response(201)
    def put(self, form_data, task_id):
        """Update a tool record on Toolhub."""
        task = Task.query.get_or_404(task_id)
        if (
            task
            and task.tool_name.decode() == form_data["tool"]
            and task.field_name.decode() == form_data["field"]
        ):
            if flask.session and flask.session["token"]:
                tool_name = form_data["tool"]
                tool_title = task.tool.title.decode()
                submission_data = build_put_request(form_data)
                token = flask.session["token"]["access_token"]
                chain(
                    make_put_request.s(tool_name, submission_data, token)
                    | check_result_status.s(form_data["field"], form_data["value"])
                    | update_db.s(task.id, form_data, tool_title)
                )()
                return "Submission sent.  Thank you for your contribution!"
            else:
                abort(401, message="User must be logged in to update a tool.")
        else:
            abort(400, message="The data given doesn't match the task specifications.")


tools = Blueprint(
    "tools", __name__, description="Get information about the tools in our database."
)


@tools.route("/api/tools/names")
class ToolNames(MethodView):
    @tools.response(200)
    def get(self):
        """Get the human-readable titles of all tools, and their Toolhub names."""
        try:
            # This will work, as long as there are no tools with the
            # title "allTitles", and no duplicate names
            # Seems improbable, but not impossible
            response = db.session.execute(text("SELECT name, title FROM tool")).all()
            titleCollection = {"allTitles": []}
            for tool in response:
                titleCollection[tool.title.decode()] = tool.name.decode()
                titleCollection["allTitles"].append(tool.title.decode())
            return titleCollection
        except exc.OperationalError as err:
            print(err)
            abort(503, message="Database connection failed.  Please try again.")


user = Blueprint(
    "user", __name__, description="Get information about the currently logged-in user."
)


@user.route("/api/user")
class CurrentUser(MethodView):
    @user.response(200, UserSchema)
    def get(self):
        """Get the username of the currently logged-in user."""
        response = get_current_user()
        if type(response) == str:
            username = {"username": response}
            return username
        else:
            return response
