import json
import logging
import os
import time
import numpy as np
import base64

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from config.mas_config import *

def create_app(test_config=None):
    """
    This function serves as a producer for the server instances
    You can call this function multiple times to produce multiple server instances
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('mas_config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    logging.info("MAS system started!")
