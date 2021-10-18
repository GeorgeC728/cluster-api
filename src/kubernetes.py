# Load libraries
from flask import Flask                             # Flask library required for API
from flask.blueprints import Blueprint              # Blueprint from flask for registerin API calls
from kubernetes import client                       # For interface with k8s API

config = client.Configuration()