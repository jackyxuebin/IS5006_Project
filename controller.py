import datetime
from threading import Lock, Thread
import threading
from multiprocessing import Process
import time

from tweepy_agent import Tweepy_Agent
from fuzzy_logic_agent import Fuzzy_Logic_Agent
from bollinger_band_agent import BollingerBandAgent
from bollinger_band_trend_agent import BollingerBandTrendAgent
from knowledge_database import knowledgeDatabase
from decider_agent import deciderAgent
from ceo import ceo
from pnl_agent import pnlAgent
from learning_agent import learningAgent

class Controller(object):
    def __init__(self):

        # Main
        self.tweepy_agent = Tweepy_Agent()
        self.knowledgeDatabase = knowledgeDatabase()
        self.ceo = ceo(self.knowledgeDatabase)
        self.pnl_agent = pnlAgent(self.knowledgeDatabase)
        self.signal_agents = [BollingerBandAgent(), BollingerBandTrendAgent(), Fuzzy_Logic_Agent()]
        self.learning_agent = learningAgent(self.knowledgeDatabase,self.signal_agents)
        self.decider_agent = deciderAgent(self.knowledgeDatabase,self.signal_agents, self.ceo)
       
        try:
            time.sleep(600)
        except KeyboardInterrupt:
            pass
