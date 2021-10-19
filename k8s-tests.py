from kubernetes import client, config                       # For interface with k8s API

#config = client.Configuration()

config.load_kube_config()

api_client = client.CoreV1Api()


#api_client = client.ApiClient(config)

namespace = "gameserver-cluster"

service = client.V1Service(
    api_version = "v1",
    kind = "Service",
    metadata = client.V1ObjectMeta(name = "minecraft", labels = {"app": "minecraft"}),
    spec = client.V1ServiceSpec(selector = {"app": "minecraft"})
)

#api_instance = client.CoreV1Api(api_client)

resp = api_client.create_namespaced_service(namespace = "default", body = service)

print(resp)