# Load libraries
from flask import Flask             # Flask libraries required for API
from healthcheck import *            # Import all calls from healthcall
from k8s_calls import *

# Create api object
api = Flask(__name__)

# Register healthcheck call
api.register_blueprint(healthcheck_call)
api.register_blueprint(k8s_calls)
# Start app
if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 50)