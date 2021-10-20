from kubernetes import client               # For creating k8s objects

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
def param_volume_claim(id, size_gb):
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
                requests = {"storage": size_gb + "Gi"}
            )
        )
    )
    # Return the volume claim
    return(volume_claim)

def param_pod_spec(id, game, ram_gb):
    pod = client.V1PodSpec(
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