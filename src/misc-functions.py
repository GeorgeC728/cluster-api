# Convert a gametype into an image name
# This could utilise a config map so different values can be used in prod/dev etc.
def get_image_name(game):
    # Return the relevant gcr container for each game
    # Could use a switch case when using 3.10
    if game == "minecraft":
        return("eu.gcr.io/server-hosting-303517/games/minecraft-java:latest")
    if game == "rust":
        return("eu.gcr.io/server-hosting-303517/games/rust:latest")
    
    return(None)