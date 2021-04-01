from threading import Lock
import pandas as pd
import google_api_agent

class knowledgeDatabase():

    def __init__(self):
        # load weights and trade_history from google sheet
        self.lock = Lock()
        self.agent_weights = {'bollinger_band_agent':1,'bollinger_band_trend_agent':1}
        self.trade_history = pd.DataFrame()

    def __del__(self):
        # save weights and trade_history to google sheet
        return None

    def get_weight(self, agent):
        # return the weight of an agent
        return self.agent_weights[agent]

    def update_weight(self, agent, weight):
        # update the weight of an agent
        self.agent_weights[agent] = weight
