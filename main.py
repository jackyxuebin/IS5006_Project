from bollinger_band_agent import BollingerBandAgent
from bollinger_band_trend_agent import BollingerBandTrendAgent
from knowledge_database import knowledgeDatabase
from decider_agent import deciderAgent
import time


knowledgeDatabase = knowledgeDatabase()
signal_agents = [BollingerBandAgent(), BollingerBandTrendAgent()]
decider_agent = deciderAgent(knowledgeDatabase,signal_agents)

try:
    time.sleep(600)
except KeyboardInterrupt:
    pass
