
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
