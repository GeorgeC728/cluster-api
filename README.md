# Game server cluster design

The game server cluster is where the customers servers will sit. Game servers will be deployed as stateful sets consisting of a single pod which will have a single container. Nodes will host DaemonSets providing SFTP access to the game server disks. A REST API will sit in the cluster providing calls to create and manage the servers.

API:
- Deployment
- Single container, multiple replicas.
- Autoscale with demand
- Python/Flask
- Will create and manage the servers.

Gameservers:
- Statefulset
- Not sure how to expose the service - maybe an external loadbalancer just to the one pod
- Disk attached for storage

File access:
- SFTP maybe SAMBA too
- DaemonSet
- Not sure how to attach pods

# Cluster API