import requests

url = "http://localhost:50"

#resp = requests.get(url = url + "/healthcheck")

#resp = requests.post(url = url + "/api/v1/server/7/create", json = {"ram_gb": 1, "disk_gb": 5})

#resp = requests.patch(url = url + "/api/v1/server/7/stop")

resp = requests.patch(url = url + "/api/v1/server/7/start")


print(resp.text)