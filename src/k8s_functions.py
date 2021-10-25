from kubernetes import client, config
from kubernetes.client.models.v1_container_port import V1ContainerPort               # For interacting with k8s API
from misc_functions import *                        # Functions that I'm not sure where else to put
import json

# Create a service for a given server name
def create_service(id, svc_name, target_name, port, target_port):
    service = client.V1Service(
        # Set API version
        api_version = "v1",
        # Set kind
        kind = "Service",
        # Create metadata
        metadata = client.V1ObjectMeta(
            name = svc_name + id,
            labels = {"app": target_name + id}),
        # Create service spec
        spec = client.V1ServiceSpec(
            type = "NodePort",
            selector = {"app": target_name + id},
            ports = [
                client.V1ServicePort(
                    protocol = "TCP",
                    port = port,
                    target_port = target_port
                )
            ])
    )
    # Return service object for deployment
    return service

# Creates the volume claim object that will form part of the statefulset
def create_volume_claim(id, disk_gb):
    volume_claim = client.V1PersistentVolumeClaim(
        metadata = client.V1ObjectMeta(
            # Create unique name of pvc
            name = "minecraft-pvc-id-" + id
        ),
        spec = client.V1PersistentVolumeClaimSpec(
            # ReadWriteOnce as rw needed and can't do multiple with a disk
            access_modes = ["ReadWriteOnce"],
            # Use SSD storage disk - maybe incorporate multiple tiers of disk oneday
            storage_class_name = "ssd-disk",
            resources = client.V1ResourceRequirements(
                # Request storage of required size
                requests = {"storage": str(disk_gb) + "Gi"}
            )
        )
    )
    # Return the volume claim
    return(volume_claim)

# pod template spec for gameservers
def create_server_pod_template_spec(id, game, ram_gb, cpu_count):
    pod = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(
                # Create unique name
                labels = {"app": "minecraft-id-" + id}
            ),
        spec = client.V1PodSpec(
            # Short termination period - probs increase in prob
            termination_grace_period_seconds = 10,
            containers = [
                # Just the one container
                client.V1Container(
                    name = "minecraft-container-id-" + id,
                    # Get the image name
                    image = get_image_name(game),
                    resources = client.V1ResourceRequirements(
                        limits = {
                            "memory": str(ram_gb) + "G",
                            "cpu": str(cpu_count * 1000) +"m"}
                    ),
                    # Mount a persistent volume so worlds are saved
                    volume_mounts = [
                        client.V1VolumeMount(
                            name = "minecraft-pvc-id-" + id,
                            # This is where the container saves world data
                            mount_path = "/data/server"
                        )
                    ],
                    # Env variables - just memory for now as its needed but defo have more later on
                    env = [
                        client.V1EnvVar(
                            name = "MEMORY",
                            value = str(round(ram_gb * 1024 * 0.8))
                        ),
                        client.V1EnvVar(
                            name = "RCON_PASSWORD",
                            value = "pass"
                        )
                    ],
                    ports = [
                        # Port for accessing server
                        client.V1ContainerPort(
                            name = "primary",
                            container_port = 25565,
                            protocol = "TCP"
                        ),
                        # Port for RCON
                        client.V1ContainerPort(
                            name = "rcon",
                            container_port = 25575,
                            protocol = "TCP"
                        )
                    ]
                )
            ]
        )
    )
    # Return the pod spec
    return(pod)

# Create pod template for the SFTP handler
def create_sftp_pod_template_spec(id):
    pod = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(
            # Unique name for the pod
            labels = {"app": "sftp-id-" + id}
        ),
        spec = client.V1PodSpec(
            volumes = [
                # Add the volume from the gameserver 
                client.V1Volume(
                    name = "sftp-volume",
                    persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
                        claim_name = "minecraft-pvc-id-" + id + "-minecraft-id-" + id + "-0"
                    )
                )
            ],
            containers = [
                # Just one cotnainer of the atmoz/sftp image
                client.V1Container(
                    name = "sftp-container-id-" + id,
                    image = "atmoz/sftp:latest",
                    args = ["user:pass:::data"],
                    # Mount the disk
                    volume_mounts = [
                        client.V1VolumeMount(
                            name = "sftp-volume",
                            mount_path = "/home/user/data"
                            #sub_path to get rid of lost+found
                        ),
                    ],
                    ports = [
                        # Primary port for sftp access
                        client.V1ContainerPort(
                            name = "primary",
                            container_port = 22,
                            protocol = "TCP"
                        )
                    ]
                )
            ]
        )
    )
    # Return the object
    return(pod)

# Spec for gameservers
def create_statefulset_spec(id, game, ram_gb, disk_gb, cpu_count):

    statefulset_spec = client.V1StatefulSetSpec(
        # Add unique selector/name
        selector = client.V1LabelSelector(
            match_labels = {"app": "minecraft-id-" + id}),
        service_name = "minecraft-id-" + id,
        # One replica - don't want more than one gameserver per set
        replicas = 1,
        # Generate template spec
        template = create_server_pod_template_spec(id, game, ram_gb, cpu_count),
        # Genearte colume claim
        volume_claim_templates = [create_volume_claim(id, disk_gb)]
    )
    # Return the object
    return(statefulset_spec)

# Spec for SFTP deployment
def create_sftp_deployment_spec(id):
    deployment_spec = client.V1DeploymentSpec(
        # Just one replica - could use more but probs not wise/necesary
        replicas = 1,
        selector = client.V1LabelSelector(
            match_labels = {"app": "sftp-id-" + id}
        ),
        # Generate pod spec
        template = create_sftp_pod_template_spec(id)
    )
    # Return object
    return(deployment_spec)

# Create the gamesverer - this will be deployed
def create_statefulset(id, game, ram_gb, disk_gb, cpu_count):

    statefulset = client.V1StatefulSet(
        api_version = "apps/v1",
        kind = "StatefulSet",
        # Unique name
        metadata = client.V1ObjectMeta(name = "minecraft-id-" + id),
        # Generate spec for server
        spec = create_statefulset_spec(id, game, ram_gb, disk_gb, cpu_count)
    )
    # Return object
    return(statefulset)

# Greate sftp deployment - this will be deployed
def create_sftp_deployment(id):

    deployment = client.V1Deployment(
        api_version = "apps/v1",
        kind = "Deployment",
        # Unique name
        metadata = client.V1ObjectMeta(name = "sftp-id-" + id),
        # Generate spec
        spec = create_sftp_deployment_spec(id)
    )

    return(deployment)

# Deploy a statefulset for a gameserver
def deploy_statefulset(id, game, ram_gb, disk_gb, cpu_count):
    # Get the statefulset object
    statefulset = create_statefulset(id, game, ram_gb, disk_gb, cpu_count)
    # Deploy it
    client.AppsV1Api().create_namespaced_stateful_set(namespace = "default", body = statefulset)

# Deploy a service - this will do both servers and sftp
def deploy_service(id, svc_name, target_name, port, target_port):
    # Create the service
    service = create_service(id, svc_name, target_name, port, target_port)
    # Deploy it
    client.CoreV1Api().create_namespaced_service(namespace = "default", body = service)

# Deploy a deployment for an sftp handler
def deploy_sftp_deployment(id):
    # Create the deployment
    deployment = create_sftp_deployment(id)
    # Deploy it
    client.AppsV1Api().create_namespaced_deployment(namespace = "default", body = deployment)

# Scale a statefulset - used for turning on/off
def scale_statefulset(id, replicas_count):
    # Patch a the given object and change the number of replicas.
    client.AppsV1Api().patch_namespaced_stateful_set_scale(
        namespace = "default",
        name = "minecraft-id-" + id,
        # Use plain ol' dict as thats what is needed
        body = {"spec":{"replicas":replicas_count}}
    )

# Returns the resource usage of a pod
def get_pod_usage(id):
    # metric API path for a pod
    metric_api = "/apis/metrics.k8s.io/v1beta1/namespaces/default/pods"
    # Run the API call - no built in functions v sad
    pod_metrics_raw = client.ApiClient().call_api(
        # Path for the resource
        metric_api + "/minecraft-id-" + str(id) + "-0",
        "GET",
        auth_settings = ['BearerToken'],
        response_type='json',
        _preload_content=False
    )[0].data.decode('utf-8')

    # Comes in plain text so convert and pull out what we want
    pod_usage = json.loads(pod_metrics_raw)["containers"][0]["usage"]

    # Return the dict
    return(pod_usage)

# Returns the resource limits of a pod
def get_pod_limits(id):
    # Extract resource limits from the pod spec
    resource_limits = client.CoreV1Api().read_namespaced_pod(
        name = "minecraft-id-7-0",
        namespace = "default").spec.containers[0].resources.limits
    
    # Return resource limits
    return(resource_limits)
