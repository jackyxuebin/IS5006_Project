import json
import logging
import os
import time
import numpy as np
import base64

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from app.utils.logger import *
from config.mas_config import *

from simulation import *


def create_app(test_config=None):
    """
    This function serves as a producer for the server instances
    You can call this function multiple times to produce multiple server instances
    """ 
    try:
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        CORS(app)
        
        flask_app_logger_agent = Logger('flask_app_logger', info_flag = True)
        flask_app_logger = flask_app_logger_agent.setup_logger('flask_app_logger', os.path.join(LOG_PATH, 'flask_app.log'), 'INFO') 
        
        if test_config is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile('mas_config.py', silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)

        logging.info("The MAS flask app has been started!")
        flask_app_logger_agent.start_logging(flask_app_logger, "The MAS flask app has been started!")

    except Exception as e:

        flask_app_logger_agent.start_logging(flask_app_logger, 'Exception - ' + str(e))
        
    @app.route('/')
    def welcome_to_group7_mas():
        """
        Simple homepage for health check
        :returns: 'Welcome to our Group 7 MAS!'
        """
        return('Welcome to our Group 7 MAS!')

    @app.route('/run_simulation')
    def run_simulation():
        
        # Start simulation
        simulation = Simulation()
        
    return app
