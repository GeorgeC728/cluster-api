# Load libraries
from flask import Flask, request                    # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client, config               # For interface with k8s API
import k8s_functions as k8s
from os import getenv

# Blueprint for this set of calls
k8s_calls = Blueprint("k8s_calls", __name__)


core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()

def authenticate():
    ENVIRONMENT = getenv("ENVIRONMENT")
    if ENVIRONMENT == "prod":
        config.load_incluster_config()
        return({"success": True})
    elif ENVIRONMENT == "dev":
        config.load_kube_config()
        return({"success": True})
    else:
        return({"success": False})

# Create a server
@k8s_calls.route("/api/v1/server/<id>/create", methods = ["POST"])
def create_server(id):
    # Convert the request into json
    data = request.get_json()

    # Create statefulset (server)
    k8s.deploy_statefulset(
        apps_v1_api,
        id = str(id),
        game = "minecraft",
        ram_gb = data["ram_gb"],
        disk_gb = data["disk_gb"])
    # Depley service for the server
    k8s.deploy_service(
        core_v1_api,
        id = str(id),
        svc_name = "minecraft-svc",
        port = 25565,
        target_port = "primary")
    # Create deployment for SFTP
    k8s.deploy_sftp_deployment(
        apps_v1_api,
        id = str(id))
    # Deploy service for SFTP
    k8s.deploy_service(
        core_v1_api,
        id = str(id),
        svc_name = "sftp",
        port = 22,
        target_port = "primary")

    return({"success": True})

@k8s_calls.route("/api/v1/server/<id>/stop", methods = ["GET"])
def stop_server(id):
    k8s.scale_statefulset(apps_v1_api, str(id), 0)

    return({"success": "much"})

@k8s_calls.route("/api/v1/server/<id>/start", methods = ["GET"])
def start_server(id):
    k8s.scale_statefulset(apps_v1_api, str(id), 1)

    return({"success": "much"})