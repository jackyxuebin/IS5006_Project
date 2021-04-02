from threading import Lock
import pandas as pd

class knowledgeDatabase():

    def __init__(self):
        # load weights and trade_history from google sheet
        self.lock = Lock()
        self.agent_weights = {'bollinger_band_agent':{1:1,0:0,-1:1},'bollinger_band_trend_agent':{1:1,0:0,-1:1}}
        self.trade_history = pd.DataFrame({'bollinger_band_agent':[0,0,0,1,1,1,-1,-1,-1],'bollinger_band_trend_agent':[0,1,-1,0,1,-1,0,1,-1],'decision':[0,0,0,1,1,1,-1,-1,-1],'profit/loss':[1,2,3,4,5,6,7,8,9]})


    def __del__(self):
        # save weights and trade_history to google sheet
        return None

    def get_weight(self, agent, signal):
        # return the weight of an agent
        return self.agent_weights[agent][signal]

    def update_weight(self, agent, weight):
        # update the weight of an agent
        self.agent_weights[agent] = weight

    def get_case(self, signals):
        # return matched case
        result = self.trade_history
        for agent,signal in signals.items():
            result = result[result[agent]==signal]
        return result