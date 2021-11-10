# Load libraries
from flask import Flask, request                    # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
import json
import pandas as pd
from urllib.request import urlopen

# Blueprint for this set of calls
games_calls = Blueprint("games_calls", __name__)

@games_calls.route("/games/minecraft/versions", methods=["GET"])
def get_version_list():
    version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

    version_manifest_json = json.loads(urlopen(version_manifest_url).read().decode('utf-8'))

    version_manifest_df = pd.DataFrame(version_manifest_json["versions"])

    version_list = version_manifest_df[["id", "type"]].to_dict(orient = "records")
    
    return({"success": True, "versions": version_list})
