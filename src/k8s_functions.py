from kubernetes import client, config
from kubernetes.client.models.v1_container_port import V1ContainerPort               # For interacting with k8s API
from misc_functions import *                        # Functions that I'm not sure where else to put

# Create a service for a given server name
def create_service(id, svc_name, port, target_port):
    service = client.V1Service(
        # Set API version
        api_version = "v1",
        # Set kind
        kind = "Service",
        # Create metadata
        metadata = client.V1ObjectMeta(
            name = svc_name + "-id-" + id,
            labels = {"app": svc_name + "-id-" + id}),
        # Create service spec
        spec = client.V1ServiceSpec(
            type = "NodePort",
            selector = {"app": svc_name + "-id-" + id},
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
                requests = {"storage": disk_gb + "Gi"}
            )
        )
    )
    # Return the volume claim
    return(volume_claim)

def create_server_pod_template_spec(id, game, ram_gb):
    pod = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(
                labels = {"app": "minecraft-id-" + id}
            ),
        spec = client.V1PodSpec(
            termination_grace_period_seconds = 10,
            containers = [
                client.V1Container(
                    name = "minecraft-container-id-" + id,
                    image = get_image_name(game),
                    volume_mounts = [
                        client.V1VolumeMount(
                            name = "minecraft-pvc-id-" + id,
                            mount_path = "/data/server"
                        )
                    ],
                    env = [
                        client.V1EnvVar(
                            name = "MEMORY",
                            value = str(ram_gb * 1024)
                        )
                    ],
                    ports = [
                        client.V1ContainerPort(
                            name = "primary",
                            container_port = 25565,
                            protocol = "TCP"
                        ),
                        client.V1ContainerPort(
                            name = "rcon",
                            container_port = 25566,
                            protocol = "TCP"
                        )
                    ]
                )
            ]
        )
    )
    # Return the pod spec
    return(pod)

def create_sftp_pod_template_spec(id):
    pod = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(
            labels = {"app": "sftp-id-" + id}
        ),
        spec = client.V1PodSpec(
            volumes = [
                client.V1Volume(
                    name = "sftp-volume",
                    persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
                        claim_name = "minecraft-pvc-id-" + id + "-minecraft-id-" + id + "-0"
                    )
                )
            ],
            containers = [
                client.V1Container(
                    name = "sftp-container-id-" + id,
                    image = "atmoz/sftp:latest",
                    args = ["user:pass:::data"],
                    volume_mounts = [
                        client.V1VolumeMount(
                            name = "sftp-volume",
                            mount_path = "/home/user/data"
                            #sub_path to get rid of lost+found
                        ),
                    ],
                    ports = [
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

    return(pod)

def create_statefulset_spec(id, game, ram_gb, disk_gb):

    statefulset_spec = client.V1StatefulSetSpec(
        selector = client.V1LabelSelector(
            match_labels = {"app": "minecraft-id-" + id}),
        service_name = "minecraft-id-" + id,
        replicas = 1,
        template = create_server_pod_template_spec(id, game, ram_gb),
        volume_claim_templates = [create_volume_claim(id, disk_gb)]
    )

    return(statefulset_spec)

def create_sftp_deployment_spec(id):

    deployment_spec = client.V1DeploymentSpec(
        replicas = 1,
        selector = client.V1LabelSelector(
            match_labels = {"app": "sftp-id-" + id}
        ),
        template = create_sftp_pod_template_spec(id)
    )

    return(deployment_spec)

def create_statefulset(id, game, ram_gb, disk_gb):

    statefulset = client.V1StatefulSet(
        api_version = "apps/v1",
        kind = "StatefulSet",
        metadata = client.V1ObjectMeta(name = "minecraft-id-" + id),
        spec = create_statefulset_spec(id, game, ram_gb, disk_gb)
    )

    return(statefulset)

def create_sftp_deployment(id):

    deployment = client.V1Deployment(
        api_version = "apps/v1",
        kind = "Deployment",
        metadata = client.V1ObjectMeta(name = "sftp-id-" + id),
        spec = create_sftp_deployment_spec(id)
    )

    return(deployment)

def deploy_statefulset(apps_v1_api, id, game, ram_gb, disk_gb):
    statefulset = create_statefulset(id, game, ram_gb, disk_gb)

    client.AppsV1Api().create_namespaced_stateful_set(namespace = "default", body = statefulset)

def deploy_service(core_v1_api, id, svc_name, port, target_port):
    service = create_service(id, svc_name, port, target_port)

    client.CoreV1Api().create_namespaced_service(namespace = "default", body = service)

def deploy_sftp_deployment(apps_v1_api, id):
    deployment = create_sftp_deployment(id)

    client.AppsV1Api().create_namespaced_deployment(namespace = "default", body = deployment)

def scale_statefulset(apps_v1_api, id, replicas_count):
    apps_v1_api.patch_namespaced_stateful_set_scale(
        namespace = "default",
        name = "minecraft-id-" + id,
        body = {"spec":{"replicas":replicas_count}}
        #body = client.V1StatefulSet(
        #    spec = client.V1StatefulSetSpec(
        #        #selector = client.V1LabelSelector(
        #        #    match_labels = {"app": "minecraft-id-" + id}),
        #        replicas = replicas_count))
    )
    #apps_v1_api.patch_namespaced_stateful_set_scale(
    #    namespace = "default",
    #    body = {"spec":{"replicas":replicas_count}}
    #)