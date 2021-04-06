from threading import Lock
from datetime import datetime
import pandas as pd
import logging
from multiagents.google_api_agent import *
import os
log = logging.getLogger('knowledge_database')

class knowledgeDatabase():

    def __init__(self):
        # load weights and trade_history from google sheet
        self.lock = Lock()
        self.agent_weights = {'bollinger_band_agent':{1:1,0:0,-1:1},'bollinger_band_trend_agent':{1:1,0:0,-1:1},'fuzzy_logic_agent':{1:1,0:0,-1:1} }
        self.trade_history = pd.DataFrame()
        self.google_api_object = Google_API_Agent()
        self.gs_name = 'PnL Report'
        self.col_num = 0

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

        header = ['action','bollinger_band_agent', 'bollinger_band_trend_agent', 'fuzzy_logic_agent', 'open_price', 'profit/loss', 'quantity', 'stoploss', 'symbol','takeprofit', 'timestamp', 'close_price']

        
        if (os.path.isfile('./local_db/pnl_data/PnL_report.csv')):
            if(self.trade_history.empty):
                pass
            else:
                self.google_api_object.append_google_sheets(self.gs_name, self.trade_history.iloc[-1,:].tolist())
                print(self.trade_history.tail(1))
                self.trade_history.tail(1).to_csv('./local_db/pnl_data/PnL_report.csv', mode='a', header=False, index=False)
        else:
            df = pd.DataFrame(columns=header)
            self.google_api_object.create_google_sheets(self.gs_name)
            self.google_api_object.append_google_sheets(self.gs_name, header)
            df.to_csv('./local_db/pnl_data/PnL_report.csv', index=False)        
        
        log.info(self.agent_weights)
        log.info(self.trade_history.head())
