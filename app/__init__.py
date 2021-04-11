import json
import logging
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import sys

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from app.utils.logger import *
from config.mas_config import *
from multiagents.simulation import *
from multiprocessing import Process

plt.rcParams["figure.figsize"] = [15, 10]

def create_app(test_config=None):
    """
    This function serves as a producer for the server instances
    You can call this function multiple times to produce multiple server instances
    """ 
    try:
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        CORS(app)
        
        simulation = ""
        
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
        print(request.environ.get('werkzeug.server.shutdown'))
        return('Welcome to our Group 7 MAS!')

    @app.route('/run_simulation')
    def run_simulation():
        
        # Start simulation
        simulation = Simulation()
        return jsonify({
            'success': True,
            'multi-agent system': 'Running',
        })

    # this api is used to plot take-profit and stop-loss against timestamp plot 
    @app.route('/takeprofit_stoploss_plot')
    def plot_takeprofit_stoploss():
        
        # Start plotting
        df = pd.read_csv('./local_db/pnl_data/PnL_report.csv', index_col = 'timestamp')
        plt.plot(df.index, df[['takeprofit']], "-b", label="Take-Profit",marker='o')
        plt.plot(df.index, df[['stoploss']], "-r", label="Stop-Loss",marker='o')
        plt.plot(df.index, df[['open_price']], "-o", label="Open Price",marker='o')
        plt.plot(df.index, df[['close_price']], "-g", label="Close Price",marker='o')

        plt.title('Take Profit vs. Stop Loss', fontsize=14)
        plt.xlabel('Timestamp', fontsize=14)
        plt.ylabel('Price', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
        plt.grid()
        plt.savefig('./local_db/visualization/Take Profit vs. Stop Loss.png', bbox_inches='tight')
        #plt.show()
        return jsonify({
            'success': True,
            'plot': 'The plot has been plotted successfully',
            'directory': '/local_db/visualization/Take Profit vs. Stop Loss.png'
        })

    # this api is used to plot suggested action and pnl against timestamp plot 
    @app.route('/action_pnl_plot')
    def plot_action_pnl():
        
        # Start plotting
        df = pd.read_csv('./local_db/pnl_data/PnL_report.csv', index_col = 'timestamp')
        plt.plot(df.index, df[['profit/loss']], "-g", label="PnL",marker='o')
        plt.plot(df.index, df[['action']], "-b", label="Acton",marker='o')

        plt.title('Suggested Action and Profit and Loss', fontsize=14)
        plt.xlabel('Timestamp', fontsize=14)
        plt.ylabel('PnL', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
        plt.grid()
        plt.savefig('./local_db/visualization/Suggested Action and Profit and Loss.png', bbox_inches='tight')
        #plt.show()
        return jsonify({
            'success': True,
            'plot': 'The plot has been plotted successfully',
            'directory': '/local_db/visualization/Suggested Action and Profit and Loss.png'
        })

    # this api is used to plot 5 signals and suggested action against timestamp plot 
    @app.route('/signals_action_plot')
    def plot_signals_action():
        
        # Start plotting
        df = pd.read_csv('./local_db/pnl_data/PnL_report.csv', index_col = 'timestamp')
        plt.plot(df.index, df[['bollinger_band_agent']], "-r", label="Bollinger Band Agent Signal",marker='D')
        plt.plot(df.index, df[['bollinger_band_trend_agent']], "-y", label="Bollinger Band Trend Agent Signal",marker='s')
        plt.plot(df.index, df[['fuzzy_logic_agent']], "-b", label="Fuzzy Logic Agent",marker='8')
        plt.plot(df.index, df[['Q_learning_double_duel_recurrent_agent']], "-c", label="Q-learning Agent",marker='o')
        plt.plot(df.index, df[['deep_evolution_agent']], "-p", label="Evolution Agent",marker='h')
        plt.plot(df.index, df[['action']], "-g", label="Acton",marker='p')

        plt.title('5 Signals and Suggested Action', fontsize=14)
        plt.xlabel('Timestamp', fontsize=14)
        plt.ylabel('Signal/Action', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
        plt.grid()
        plt.savefig('./local_db/visualization/5 Signals and Suggested Action.png', bbox_inches='tight')
        #plt.show()
        return jsonify({
            'success': True,
            'plot': 'The plot has been plotted successfully',
            'directory': '/local_db/visualization/5 Signals and Suggested Action.png'
        })

    @app.route('/cumulative_profit_plot')
    def plot_cumulative_profit():
        df = pd.read_csv('./local_db/pnl_data/PnL_report.csv', index_col='timestamp')
        df['profit/loss'].dropna().cumsum().plot()
        plt.title('Cumulative profit/loss over time', fontsize=14)
        plt.xlabel('Timestamp', fontsize=14)
        plt.ylabel('Cumulative profit/loss', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
        plt.grid()
        plt.savefig('./local_db/visualization/Cumulative Profit.png', bbox_inches='tight')
        #plt.show()
        return jsonify({
            'success': True,
            'plot': 'The plot has been plotted successfully',
            'directory': '/local_db/visualization/Cumulative Profit.png'
        })
   
    return app
