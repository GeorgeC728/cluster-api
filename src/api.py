# Load libraries
# Libraries
from flask import Flask             # Flask libraries required for API
from healthcheck import *           # Import all calls from healthcall
from dotenv import load_dotenv      # Import env variables from .env
import os                           # Call env variables
# Custom scripts
from k8s_calls import *             # Interfacing with k8s API
from games_calls import *           # Calling info about games

# Load .env
load_dotenv()
authenticate()
# Create api object
api = Flask(__name__)

# Register healthcheck call
api.register_blueprint(healthcheck_call)
api.register_blueprint(k8s_calls)
api.register_blueprint(games_calls)

# Start app
if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 50)