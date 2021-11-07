import re
import json
import pandas as pd
from urllib.request import urlopen

# Convert a gametype into an image name
# This could utilise a config map so different values can be used in prod/dev etc.
def get_image_name(game):
    # Return the relevant gcr container for each game
    # Could use a switch case when using 3.10
    if game == "minecraft":
        return("eu.gcr.io/server-hosting-303517/games/minecraft-java:latest")
    if game == "rust":
        return("eu.gcr.io/server-hosting-303517/games/rust:latest")
    
    # Return None if not found - can use better error handling
    return(None)

# Convert units like "Ki" or "K" to bytes
def convert_to_bytes(value):

    
    if re.search("[a-zA-Z]+", value):
        unit = re.search("[a-zA-Z]+", value).group(0)
    else:
        unit = ""

    # Ki is in powers of 2, 1024 bytes
    # K is SI, 1000 bytes
    if unit == "Ki":
        # 2 ** 10 = 1021 = 1 kb
        bytes = 2 ** 10
    elif unit == "K":
        bytes = 1e3
    elif unit == "Mi":
        bytes = 2 ** 20
    elif unit == "M":
        bytes = 1e6
    elif unit == "Gi":
        bytes = 2 ** 30
    elif unit == "G":
        bytes = 1e9
    elif unit == "Ti":
        bytes = 2 ** 40
    elif unit == "T":
        bytes = 1e12
    else:
        # if not recognised there probably wasn't a unit supplied
        bytes = 1
    
    # Return it
    return(bytes * int(value.replace(unit, "")))

# Convert vCPU units to orders of 1
def convert_to_vcpu(value):
    if re.search("[a-zA-Z]+", value):
        unit = re.search("[a-zA-Z]+", value).group(0)
    else:
        unit = ""

    if unit == "n":
        vcpus = 1e-9
    elif unit == "m":
        vcpus = 1e-3
    else:
        vcpus = 1
    
    return(vcpus * int(value.replace(unit, "")))

# Get a version link from a version name
def get_version_link(version):
    # Link to mojangs version page
    version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    # Extract JSON from the version manifest
    version_manifest_json = json.loads(urlopen(version_manifest_url).read().decode('utf-8'))
    # Convert to dataframe
    version_manifest_df = pd.DataFrame(version_manifest_json["versions"])
    # Get the link to the desired veersion
    url = version_manifest_df[version_manifest_df["id"] == version]["url"].values[0]
    # Return the link
    return(url)