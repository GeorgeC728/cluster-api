# Load libraries
from flask import Flask, request                    # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client, config               # For interface with k8s API
import k8s_functions as k8s
from os import getenv

# Blueprint for this set of calls
k8s_calls = Blueprint("k8s_calls", __name__)

# Authenticate with k8s API
def authenticate():
    # Get the envrionment env variable - tells us if its prod or dev
    ENVIRONMENT = getenv("ENVIRONMENT")
    if ENVIRONMENT == "prod":
        # If prod use the includer config
        config.load_incluster_config()
        return({"success": True})
    elif ENVIRONMENT == "dev":
        # If dev use the hosts config file - kubectl needs to be configured for this to work
        config.load_kube_config()
        return({"success": True})
    else:
        # If neither don't authenticate - it's not been entered (correctly)
        return({"success": False})

# Create a server
@k8s_calls.route("/api/v1/server/<id>/create", methods = ["POST"])
def create_server(id):
    # Convert the request into json
    data = request.get_json()

    # Create statefulset (server)
    k8s.deploy_statefulset(
        id = str(id),
        game = "minecraft",
        ram_gb = data["ram_gb"],
        disk_gb = data["disk_gb"])
    # Deploy service for the server
    k8s.deploy_service(
        id = str(id),
        svc_name = "minecraft-primary-",
        target_name = "minecraft-id-",
        port = 25565,
        target_port = "primary")
    # Deploy service for RCON
    k8s.deploy_service(
        id = str(id),
        svc_name = "minecraft-rcon-",
        target_name = "minecraft-id-",
        port = 25575,
        target_port = "rcon")
    # Create deployment for SFTP
    k8s.deploy_sftp_deployment(
        id = str(id))
    # Deploy service for SFTP
    k8s.deploy_service(
        id = str(id),
        svc_name = "sftp",
        target_name = "sftp-",
        port = 22,
        target_port = "primary")

    return({"success": True})

# Stop a server
@k8s_calls.route("/api/v1/server/<id>/stop", methods = ["PATCH"])
def stop_server(id):
    # Scale the statefulset to 0 to turn off
    k8s.scale_statefulset(str(id), 0)

    return({"success": True})

# Start a server
@k8s_calls.route("/api/v1/server/<id>/start", methods = ["PATCH"])
def start_server(id):
    # Scale statefulset to 1 to turn back on
    k8s.scale_statefulset(str(id), 1)

    return({"success": True})

# Delete server
@k8s_calls.route("/api/v1/server/<id>/delete", methods = ["DELETE"])
def delete_server(id):
    # Delete the server
    client.AppsV1Api().delete_namespaced_stateful_set(
        name = "minecraft-id-" + str(id),
        namespace = "default"
        )
    # Delete sftp
    client.AppsV1Api().delete_namespaced_deployment(
        name = "sftp-id-" + str(id),
        namespace = "default"
        )
    # Delete the server service
    client.CoreV1Api().delete_namespaced_service(
        name = "minecraft-primary-" + str(id),
        namespace = "default"
        )
    # Delete the server rcon service
    client.CoreV1Api().delete_namespaced_service(
        name = "minecraft-rcon-" + str(id),
        namespace = "default"
        )
    # Delete the sftp service
    client.CoreV1Api().delete_namespaced_service(
        name = "sftp-id-" + str(id),
        namespace = "default"
        )
    # Delete the pvc
    client.CoreV1Api().delete_namespaced_persistent_volume_claim(
        name = "minecraft-pvc-id-" + str(id) + "-minecraft-id-" + str(id) + "-0",
        namespace = "default"
        )
    
    return({"success": True})
