# Game server cluster design

The game server cluster is where the customers servers will sit. Game servers will be deployed as stateful sets consisting of a single pod which will have a single container. Nodes will host DaemonSets providing SFTP access to the game server disks. A REST API will sit in the cluster providing calls to p and manage the servers.

API:
- Deployment
- Single container, multiple replicas.
- Autoscale with demand
- Python/Flask
- Will p and manage the servers.

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
|Path|/api/v1/server/`id`/|
|Method|POST|
|Parameters|`{ram_gb:, disk_gb:}`|
|Returns|`{success: True}`|

Creates a server - just minecraft at the moment.

### Start server

|||
|---|---|
|Path|/api/v1/server/`id`/start|
|Method|PATCH|
|Parameters||
|Returns|`{success: True}`|

Starts the server associated with the id

### Stop server

|||
|---|---|
|Path|/api/v1/server/`id`/stop|
|Method|PATCH|
|Parameters||
|Returns|`{success: True}`|

Stops the server associated with the id

### Ports

|||
|---|---|
|Path|/api/v1/server/`id`/port/`type`|
|Method|PATCH|
|Parameters|`type` takes either `primary` for the main gameserver port, `rcon` for the rcon port and `sftp` for the sftp port|
|Returns|`{success: True, port:}`|


## Variable glossary

|Variable|Data type|Accepted values|Description|
|---|---|---|---|
|success|bool|True, False|Whether the request was successful|
|id|int||The ID of the server - accepts int but currently converted to string when used|
|game|str|minecraft| The name of the game|
|ram_gb|int||The ram for the server in GB|
|disk_gb|int||The disk space for the server in GB|
