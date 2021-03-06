import datetime
from threading import Lock, Thread
import threading
from multiprocessing import Process
import time

from multiagents.tweepy_agent import Tweepy_Agent
from multiagents.fuzzy_logic_agent import Fuzzy_Logic_Agent
from multiagents.bollinger_band_agent import BollingerBandAgent
from multiagents.deep_evolution_agent import DeepEvolutionAgent
from multiagents.Q_learning_double_duel_recurrent_agent import QLearningDoubleDuelRecurrentAgent
from multiagents.bollinger_band_trend_agent import BollingerBandTrendAgent
from multiagents.knowledge_database import knowledgeDatabase
from multiagents.decider_agent import deciderAgent
from multiagents.ceo import ceo
from multiagents.pnl_agent import pnlAgent
from multiagents.learning_agent import learningAgent
from app.constants.constants import log_level
import logging

class Controller(object):
    def __init__(self):

        # Main
        if log_level == 'WARN':
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.WARN)
        else:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)
        self.tweepy_agent = Tweepy_Agent()
        self.knowledgeDatabase = knowledgeDatabase()
        self.ceo = ceo(self.knowledgeDatabase)
        self.pnl_agent = pnlAgent(self.knowledgeDatabase)
        self.signal_agents = [BollingerBandAgent(), BollingerBandTrendAgent(), Fuzzy_Logic_Agent(), DeepEvolutionAgent(), QLearningDoubleDuelRecurrentAgent()]
        self.learning_agent = learningAgent(self.knowledgeDatabase,self.signal_agents)
        self.decider_agent = deciderAgent(self.knowledgeDatabase,self.signal_agents, self.ceo)
       
        #try:
        #    time.sleep(600)
        #except KeyboardInterrupt:
        #    pass
