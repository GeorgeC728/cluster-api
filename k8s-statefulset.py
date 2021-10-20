from kubernetes import client, config
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_stateful_set_spec import V1StatefulSetSpec
from kubernetes.client.models.v1_volume_mount import V1VolumeMount                       # For interface with k8s API

config.load_kube_config()

api_client = client.AppsV1Api()

statefulset = client.V1StatefulSet(
    api_version = "apps/v1",
    kind = "StatefulSet",
    metadata = client.V1ObjectMeta(name = "minecraft"),
    spec = client.V1StatefulSetSpec(
        selector = client.V1LabelSelector(
            match_labels = {"app": "minecraft"}),
        service_name = "minecraft",
        replicas = 1,
        template = client.V1PodTemplateSpec(
            metadata = client.V1ObjectMeta(
                labels = {"app": "minecraft"}),
            spec = client.V1PodSpec(
                termination_grace_period_seconds = 180,
                containers = [
                    client.V1Container(
                        name = "minecraft-server",
                        image = "eu.gcr.io/server-hosting-303517/games/minecraft-java:latest",
                        volume_mounts = [
                            client.V1VolumeMount(
                                name = "minecraft-data",
                                mount_path = "/data/server",
                            )
                        ],
                        env = [
                            client.V1EnvVar(
                                name = "MEMORY",
                                value = "2000")]
                    )]
            )),
        volume_claim_templates = [
            client.V1PersistentVolumeClaim(
                metadata = V1ObjectMeta(
                    name = "minecraft-data"
                ),
                spec = client.V1PersistentVolumeClaimSpec(
                    access_modes = ["ReadWriteOnce"],
                    storage_class_name = "ssd-disk",
                    resources = client.V1ResourceRequirements(
                        requests = {"storage": "1Gi"}
                    )
                )
            )
        ]
    )
)

api_client.create_namespaced_stateful_set(namespace = "default", body = statefulset)