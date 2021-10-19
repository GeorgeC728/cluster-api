# Load libraries
from flask import Flask                             # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client, config               # For interface with k8s API
import k8s_functions as k8s

# Blueprint for this set of calls
k8s_calls = Blueprint("k8s_calls", __name__)


config.load_kube_config()

api_client = client.CoreC1Api()

@k8s_calls.route("/v1/create-server/", methods = ["POST"])
def create_server():
    # Function to create server
    k8s.create_service(api_client, "minecraft")