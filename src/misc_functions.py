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
def convert_to_bytes(unit):
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
    return(bytes)