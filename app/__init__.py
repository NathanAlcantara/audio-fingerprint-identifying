import json

import click
from flask import Flask, redirect
from flask_graphql import GraphQLView
from flask_migrate import Migrate

from .config import config_logger, graphql_logging_middleware
from .graphql import schema
from .models import db

config_logger()

app = Flask(__name__)
app.config.from_file("config/config.json", load=json.load)

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def root():
    return redirect("/graphql")


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphq",
        schema=schema,
        graphiql=True,
        middleware=[graphql_logging_middleware],
    ),
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
