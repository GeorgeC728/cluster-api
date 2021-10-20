# Load libraries
from flask import Flask             # Flask libraries required for API
from healthcheck import *            # Import all calls from healthcall

# Create api object
api = Flask(__name__)

# Register healthcheck call
api.register_blueprint(healthcheck_call)

@api.route("/api/v1/server/<id>/create")
def create_server(id):
    return({"id": id})

# Start app
if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 50)