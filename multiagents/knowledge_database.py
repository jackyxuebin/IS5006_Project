from threading import Lock
from datetime import datetime
import pandas as pd
import logging
from multiagents.google_api_agent import *
import os
import numpy as np
log = logging.getLogger('knowledge_database')

class knowledgeDatabase():

    def __init__(self):
        # load weights and trade_history from google sheet
        self.lock = Lock()
        
        if (os.path.isfile('./knowledge_data/agent_weights.csv')):
            self.agent_weights = pd.read_csv('./knowledge_data/agent_weights.csv',index_col=0).to_dict()
            print('The agent weights have been loaded')
        else:
            self.agent_weights = {'bollinger_band_agent':{1:1,0:0,-1:1}, 'bollinger_band_trend_agent':{1:1,0:0,-1:1},'fuzzy_logic_agent':{1:1,0:0,-1:1}, 'deep_evolution_agent':{1:1,0:0,-1:1}, 'Q_learning_double_duel_recurrent_agent':{1:1,0:0,-1:1} }
            print('The default agent weights have been loaded')
            
        if (os.path.isfile('./local_db/pnl_data/PnL_report.csv')):
            self.trade_history = pd.read_csv('./local_db/pnl_data/PnL_report.csv')
            print('The PnL records have been loaded')

        else:
            self.trade_history = pd.DataFrame()
            print('No PnL records have been loaded')
        
        self.google_api_object = Google_API_Agent()
        self.gs_name_pnl = 'PnL Report'
        self.gs_name_weights = 'Agent Weights'
        self.google_sheets_created_pnl = 0
        self.google_sheets_created_weights = 0
        self.df_size = 0
        self.temp_size = 0

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

        header = ['timestamp', 'symbol', 'action', 'bollinger_band_agent', 'bollinger_band_trend_agent', 'fuzzy_logic_agent', 'deep_evolution_agent', 'Q_learning_double_duel_recurrent_agent','open_price', 'close_price', 'quantity', 'profit/loss',  'stoploss', 'takeprofit']
        header_weights = ['bollinger_band_agent', 'bollinger_band_trend_agent', 'fuzzy_logic_agent', 'deep_evolution_agent', 'Q_learning_double_duel_recurrent_agent']
        
        # rearrange the columns
        if('close_price' in self.trade_history.columns and self.trade_history.empty):
            self.trade_history = self.trade_history[header]
            
        elif('close_price' not in self.trade_history.columns and not self.trade_history.empty):
            self.trade_history = self.trade_history[header]
            
        elif('close_price' in self.trade_history.columns and not self.trade_history.empty):
            self.trade_history = self.trade_history[header]
        else:
            pass

        # write to both local database and Google Sheets
        if (os.path.isfile('./local_db/pnl_data/PnL_report.csv')):
            if(self.trade_history.empty):
                pass
            else:
                self.df_size = len(self.trade_history)
                if(self.df_size > self.temp_size):
                    self.google_api_object.append_google_sheets(self.gs_name_pnl, self.trade_history.iloc[-1,:].tolist())
                    self.trade_history.tail(1).to_csv('./local_db/pnl_data/PnL_report.csv', mode='a', header=False, index=False)
                    self.temp_size = len(self.trade_history)
                else:
                    pass
        else:
            if(self.google_sheets_created_pnl == 0):
                df = pd.DataFrame(columns=header)
                self.google_api_object.create_google_sheets(self.gs_name_pnl)
                self.google_api_object.append_google_sheets(self.gs_name_pnl, header)
                df.to_csv('./local_db/pnl_data/PnL_report.csv', index=False)
                self.google_sheets_created_pnl += 1
            else:
                pass
            
        
        df_agent_weights = pd.DataFrame.from_dict(self.agent_weights)
        df_agent_weights['action'] = df_agent_weights.index
        df_agent_weights.reset_index(inplace=True,drop=True)
        df_agent_weights.to_csv('./local_db/knowledge_data/agent_weights.csv', index=True)

        if(self.google_sheets_created_weights == 0):
            self.google_api_object.create_google_sheets(self.gs_name_weights)
            self.google_sheets_created_weights += 1
        else:
            pass
        
        self.google_api_object.write_google_sheets(self.gs_name_weights, df_agent_weights)
        
        log.info(self.agent_weights)
        log.info(self.trade_history.head())
