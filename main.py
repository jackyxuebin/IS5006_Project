from bollinger_band_agent import BollingerBandAgent
from bollinger_band_trend_agent import BollingerBandTrendAgent
from knowledge_database import knowledgeDatabase
from decider_agent import deciderAgent
from ceo import ceo
from pnl_agent import pnlAgent
from learning_agent import learningAgent
import time
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.DEBUG)
knowledgeDatabase = knowledgeDatabase()
ceo = ceo(knowledgeDatabase)
pnl_agent = pnlAgent(knowledgeDatabase)
signal_agents = [BollingerBandAgent(), BollingerBandTrendAgent()]
learning_agent = learningAgent(knowledgeDatabase,signal_agents)
decider_agent = deciderAgent(knowledgeDatabase,signal_agents, ceo)



try:
    time.sleep(600)
except KeyboardInterrupt:
    pass
