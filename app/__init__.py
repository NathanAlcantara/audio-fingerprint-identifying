import json

import click
from flask import Flask, redirect
from flask_migrate import Migrate
from graphene_file_upload.flask import FileUploadGraphQLView

from .configs import config_logger, graphql_logging_middleware
from .graphql import schema
from .models import db, initialize_database

config_logger()

app = Flask(__name__)
app.config.from_file("configs/config.json", load=json.load)

db.init_app(app)
migrate = Migrate(app, db)

@app.cli.command("initdb")
def initdb():
    initialize_database(app)


@app.route("/")
def root():
    return redirect("/graphql")


app.add_url_rule(
    "/graphql",
    view_func=FileUploadGraphQLView.as_view(
        "graphq",
        schema=schema,
        graphiql=True,
        middleware=[graphql_logging_middleware],
    ),
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
