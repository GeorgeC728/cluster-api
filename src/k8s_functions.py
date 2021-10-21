from kubernetes import client, config               # For interacting with k8s API
from misc_functions import *                        # Functions that I'm not sure where else to put

# Create a service for a given server name
def create_service(client, server_name):
    service = client.V1Service(
        # Set API version
        api_version = "v1",
        # Set kind
        kind = "Service",
        # Create metadata
        metadata = client.V1ObjectMeta(
            name = server_name,
            labels = {"app": server_name}),
        # Create service spec
        spec = client.V1ServiceSpec(
            selector = {"app": server_name},
            cluster_ip = "None")
    )
    # Return service object for deployment
    return service

# Creates the volume claim object that will form part of the statefulset
def param_volume_claim(id, disk_gb):
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
                requests = {"storage": disk_gb + "Gi"}
            )
        )
    )
    # Return the volume claim
    return(volume_claim)

def param_pod_template_spec(id, game, ram_gb):
    pod = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(
                labels = {"app": "minecraft-id-" + id}
            ),
        spec = client.V1PodSpec(
            termination_grace_period_seconds = 180,
            containers = [
                client.V1Container(
                    name = "minecraft-container-id-" + id,
                    image = get_image_name(game),
                    volume_mounts = [
                        client.V1VolumeMount(
                            name = "minecraft-pvc-" + id,
                            mount_path = "/data/server"
                        )
                    ],
                    env = [
                        client.V1EnvVar(
                            name = "MEMORY",
                            value = str(ram_gb * 1024)
                        )
                    ]
                )
            ]
        )
    )
    # Return the pod spec
    return(pod)

def param_statefulset_spec(id, game, ram_gb, disk_gb):

    statefulset_spec = client.V1StatefulSetSpec(
        selector = client.V1LabelSelector(
            match_labels = {"app": "minecraft-id-" + id}),
        service_name = "minecraft-id-" + id,
        replicas = 1,
        template = param_pod_template_spec(id, game, ram_gb),
        volume_claim_templates = [param_volume_claim(id, disk_gb)]
    )

    return(statefulset_spec)

def param_statefulset(id, game, ram_gb, disk_gb):

    statefulset = client.V1StatefulSet(
        api_versionn = "apps/v1",
        kind = "StatefulSet",
        metadata = client.V1ObjectMeta(name = "minecraft-id-" + id),
        spec = param_statefulset_spec(id, game, ram_gb)
    )

    return(statefulset)

def create_statefulset(id, game, ram_gb, disk_gb):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    statefulset = param_statefulset(id, game, ram_gb, disk_gb)

    apps_v1_api.create_namespaced_stateful_set(namespace = "default", body = statefulset)