# Load libraries
from flask import Flask, request                    # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client, config               # For interface with k8s API
import k8s_functions as k8s
from os import getenv
from misc_functions import *

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
        disk_gb = data["disk_gb"],
        cpu_count = data["cpu_count"])
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
        target_name = "sftp-id-",
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

@k8s_calls.route("/api/v1/server/<id>/restart", methods = ["PATCH"])
def restart_server(id):
    # Restart can be done by just stopping and starting straight away
    stop_server(id)
    start_server(id)
    # Return success
    return({"success": True})

# Delete server
@k8s_calls.route("/api/v1/server/<id>/delete", methods = ["DELETE"])
def delete_server(id):
    # Delete the server
    client.AppsV1Api().delete_namespaced_stateful_set(
        name = "minecraft-id-" + str(id),
        namespace = getenv("NAMESPACE")
        )
    # Delete sftp
    client.AppsV1Api().delete_namespaced_deployment(
        name = "sftp-id-" + str(id),
        namespace = getenv("NAMESPACE")
        )
    # Delete the server service
    client.CoreV1Api().delete_namespaced_service(
        name = "minecraft-primary-" + str(id),
        namespace = getenv("NAMESPACE")
        )
    # Delete the server rcon service
    client.CoreV1Api().delete_namespaced_service(
        name = "minecraft-rcon-" + str(id),
        namespace = getenv("NAMESPACE")
        )
    # Delete the sftp service
    client.CoreV1Api().delete_namespaced_service(
        name = "sftp" + str(id),
        namespace = getenv("NAMESPACE")
        )
    # Delete the pvc
    client.CoreV1Api().delete_namespaced_persistent_volume_claim(
        name = "minecraft-pvc-id-" + str(id) + "-minecraft-id-" + str(id) + "-0",
        namespace = getenv("NAMESPACE")
        )
    
    return({"success": True})


# Get the port that the server/rcon/sftp is running on
@k8s_calls.route("/api/v1/server/<id>/port/<type>", methods = ["GET"])
def get_sftp_port(id, type):
    
    if type == "primary":
        name = "minecraft-primary-" + str(id)
    elif type == "rcon":
        name = "minecraft-rcon-" + str(id)
    elif type == "sftp":
        name = "sftp" + str(id)
    
    # Get object representing the service
    service = client.CoreV1Api().read_namespaced_service(
        name = name,
        namespace = getenv("NAMESPACE"))
    
    # Extract the port from the service object
    port = service.spec.ports[0].node_port
    
    # Return
    return({"success": True, "port": port})

@k8s_calls.route("/api/v1/server/<id>/status", methods = ["GET"])
def get_status(id):
    replicas_count = client.AppsV1Api().read_namespaced_stateful_set(
        name = "minecraft-id-" + str(id),
        namespace = getenv("NAMESPACE")
    ).spec.replicas

    if replicas_count == 0:
        return({"success": True, "status": "Not running"})
    if replicas_count == 1:
        status = client.CoreV1Api().read_namespaced_pod(
            name = "minecraft-id-" + str(id) + "-0",
            namespace = getenv("NAMESPACE")
        ).status.phase
        return({"success": True, "status": status})
    else:
        return({"success": False})
    

    return({"success": False})

@k8s_calls.route("/api/v1/server/<id>/usage", methods = ["GET"])
def get_usage(id):
    # Usage stats
    pod_usage = k8s.get_pod_usage(id)
    # Limit stats
    pod_limits = k8s.get_pod_limits(id)

    # Create empty dict to store the return
    resource_usage = dict()

    # Get the CPU usage
    cpu_usage = convert_to_vcpu(pod_usage["cpu"])
    # Store in return
    resource_usage["cpu_usage"] = cpu_usage
    # Get memory usage in GB
    memory_usage = convert_to_bytes(pod_usage["memory"]) / 2 ** 30
    # Store in return
    resource_usage["memory_usage_gb"] = memory_usage
    # Get the CPU limits
    #cpu_limits =  convert_to_vcpu(pod_limits["cpu"])
    cpu_limits = 2
    # Store in return
    resource_usage["cpu_limits"] = cpu_limits
    # Get memory limits in GB
    memory_limits = convert_to_bytes(pod_limits["memory"]) / 1e9
    # Store in return
    resource_usage["memory_limits_gb"] = memory_limits
    resource_usage["cpu_percent"] = cpu_usage / cpu_limits
    resource_usage["memory_percent"] = memory_usage / memory_limits
    # Store the success
    resource_usage["success"] = True
    # Return the memory usage
    return(resource_usage)