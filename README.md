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

## API management

This section includes the API calls that are used to manage the API itself

### Healthcheck

|||
|---|---|
|Path|/healthcheck|
|Parameters||
|Returns|`{alive:True}`|

This can be used to ensure that the API is up and able to accept requests.

## Creating and removing servers

### Create server

|||
|---|---|
|Path|/api/v1/server/id/create|
|Method|POST|
|Parameters|`{game:, ram_gb:, disk_gb:}`|
|Returns|`{success: True}`|




## Variable glossary

|Variable|Data type|Accepted values|Description|
|---|---|---|---|
|success|bool|True, False|Whether the request was successful|
|id|int||The ID of the server|
|game|str|minecraft, rust| The name of the game|
