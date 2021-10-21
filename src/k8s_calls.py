# Load libraries
from flask import Flask                             # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client, config               # For interface with k8s API
import k8s_functions as k8s

# Blueprint for this set of calls
k8s_calls = Blueprint("k8s_calls", __name__)


config.load_kube_config()

core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()

@k8s_calls.route("/v1/server/<id>/create", methods = ["GET"])
def create_server(id):
    # Function to create server
    #k8s.create_service(api_client, "minecraft")
    k8s.deploy_statefulset(apps_v1_api, id = str(id), game = "minecraft", ram_gb = 2, disk_gb = "5")
    k8s.deploy_service(core_v1_api, str(id))

    return({"success": "much"})

@k8s_calls.route("/v1/server/<id>/stop", methods = ["GET"])
def stop_server(id):
    k8s.scale_statefulset(apps_v1_api, str(id), 0)

    return{"success": "much"}

@k8s_calls.route("/v1/server/<id>/start", methods = ["GET"])
def start_server(id):
    k8s.scale_statefulset(apps_v1_api, str(id), 1)

    return{"success": "much"}