from threading import Lock
import pandas as pd
import numpy as np

class knowledgeDatabase():

    def __init__(self):
        # load weights and trade_history from google sheet
        self.lock = Lock()
        self.agent_weights = {'bollinger_band_agent':{1:1,0:0,-1:1},'bollinger_band_trend_agent':{1:1,0:0,-1:1}}
        self.trade_history = pd.DataFrame()


    def __del__(self):
        # save weights and trade_history to google sheet
        return None

    def get_weight(self, agent, signal):
        # return the weight of an agent

        return self.agent_weights[agent][signal]


    def update_weight(self, agent, weight):
        # update the weight of an agent
        self.lock.acquire()
        self.agent_weights[agent] = weight
        self.lock.release()

    def get_case(self, signals):
        # return matched case
        result = self.trade_history
        if len(result) ==0:
            return result

        for agent,signal in signals.items():
            result = result[result[agent]==signal]

        return result

    def get_open_trades(self):
        if len(self.trade_history) == 0:
            return self.trade_history
        else:
            print()
            return self.trade_history[self.trade_history['profit/loss'].isnull()]

    def record_trade(self, trade_entry):
        self.lock.acquire()
        self.trade_history = self.trade_history.append(trade_entry, ignore_index=True)
        self.lock.release()

    def get_agg_pnl(self, agent, action, isProfit):
        # gets the aggregated profit or loss for an agent

        if len(self.trade_history) == 0:
            return 0
        # first find all records when agent predict action(buy/sell)
        df = self.trade_history[self.trade_history[agent]==action]
        # filter records where the predicted action is the final action of the trade
        df = df[df['action']==action]
        if isProfit:
            df = df[df['profit/loss']>=0]
        else:
            df = df[df['profit/loss']<0]
        return df['profit/loss'].dropna().sum()

    def update_pnl(self, index, closing_price, pnl):
        self.lock.acquire()
        self.trade_history.at[index,'close_price']=closing_price
        self.trade_history.at[index,'profit/loss']=pnl
        self.lock.release()

    def dump(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns',None)
        print(self.agent_weights)
        print(self.trade_history.head())