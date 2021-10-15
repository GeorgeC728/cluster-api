# Load libraries
from flask import Flask                             # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls

# Blueprint for this files functions
healthcheck_call = Blueprint("healthcheck_call", __name__)

# Healthcheck all - returns alive: True as a check for the API being up
@healthcheck_call.route("/healthcheck", methods = ["GET"])
def health_check():
    return({"alive": True})
