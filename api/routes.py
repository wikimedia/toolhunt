import flask

from celery import chain
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import desc, exc, func, text

from api import db
from api.async_tasks import make_put_request, process_result
from api.models import Field, Task
from api.schemas import (
    ContributionLimitSchema,
    ContributionSchema,
    ContributionsMetricsSchema,
    FieldSchema,
    ScoreLimitSchema,
    ScoreSchema,
    TaskCompleteSchema,
    TaskSchema,
    TasksMetricsSchema,
    ToolsMetricsSchema,
    UserMetricsSchema,
    UserSchema,
)
from api.utils import ToolhubClient, build_request, generate_past_date, get_current_user

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
            return (
                Task.query.filter(Task.user.is_not(None))
                .order_by(desc(Task.timestamp))
                .limit(int(limit))
            )
        else:
            return Task.query.filter(Task.user.is_not(None)).order_by(
                desc(Task.timestamp)
            )


@contributions.route("/api/contributions/<string:user>")
class ContributionsByUser(MethodView):
    @contributions.response(200, ContributionSchema(many=True))
    def get(self, user):
        """List the ten most recent contributions by a user."""
        # Ideally in the future we could introduce pagination and return all of a user's contributions
        return (
            Task.query.filter(Task.user == user)
            .order_by(desc(Task.timestamp))
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
                "SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL AND timestamp >= :date GROUP BY user ORDER BY 2 DESC LIMIT 30"
            ).bindparams(date=end_date)
        else:
            scores_query = text(
                "SELECT DISTINCT user, COUNT(*) AS 'score' FROM task WHERE user IS NOT NULL GROUP BY user ORDER BY 2 DESC LIMIT 30"
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
                text("SELECT COUNT(*) FROM task WHERE user IS NOT NULL")
            ).all()
            results["Total_contributions"] = total[0][0]
            thirty_day = db.session.execute(
                text(
                    "SELECT COUNT(*) FROM task WHERE user IS NOT NULL AND timestamp >= :date"
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
            total = db.session.execute(text("SELECT COUNT(*) FROM task")).all()
            results["Number_of_tasks_in_the_Toolhunt_database"] = total[0][0]
            incomplete = db.session.execute(
                text("SELECT COUNT(*) FROM task WHERE user IS NULL")
            ).all()
            results["Number_of_unfinished_tasks_in_the_Toolhunt_database"] = incomplete[
                0
            ][0]
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
            total = db.session.execute(text("SELECT COUNT(*) FROM tool")).all()
            results["Number_of_tools_on_record"] = total[0][0]
            missing_info = db.session.execute(
                text("SELECT COUNT(DISTINCT tool_name) FROM task WHERE user IS NULL")
            ).all()
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
                    text("SELECT COUNT(*) FROM task WHERE user = :user").bindparams(
                        user=user
                    )
                ).all()
                results["My_total_contributions"] = total_cont[0][0]
                thirty_cont = db.session.execute(
                    text(
                        "SELECT COUNT(*) FROM task WHERE user = :user AND timestamp >= :date"
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
        return Task.query.filter(Task.user.is_(None)).order_by(func.random()).limit(10)


@tasks.route("/api/tasks/<string:task_id>")
class TaskById(MethodView):
    @tasks.response(200, TaskSchema)
    def get(self, task_id):
        """Get information about a specific task."""
        task = Task.query.get_or_404(task_id)
        return task

    @tasks.arguments(TaskCompleteSchema)
    @tasks.response(201)
    def put(self, form_data, task_id):
        """Update a tool record on Toolhub."""
        task = Task.query.get_or_404(task_id)
        if (
            task
            and task.tool_name == form_data["tool"]
            and task.field_name == form_data["field"]
        ):
            if task.user is not None:
                abort(409, message="This task has already been completed.")
            elif flask.session and flask.session["token"]:
                tool_name = form_data["tool"]
                submission_data = build_request(form_data)
                token = flask.session["token"]["access_token"]
                chain(make_put_request.s(tool_name, submission_data, token) | process_result.s(task.id, form_data["field"], form_data["value"]))()
                return "Task sent."
            else:
                abort(401, message="User must be logged in to update a tool.")
        else:
            abort(400, message="The data given doesn't match the task specifications.")


user = Blueprint(
    "user", __name__, description="Get information about the currently logged-in user."
)


@user.route("/api/user")
class CurrentUser(MethodView):
    @tasks.response(200, UserSchema)
    def get(self):
        """Get the username of the currently logged-in user."""
        response = get_current_user()
        if type(response) == str:
            username = {"username": response}
            return username
        else:
            return response
