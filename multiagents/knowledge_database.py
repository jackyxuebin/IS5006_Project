import logging
from multiagents.google_api_agent import *
import os
from threading import Thread
from app.constants.constants import tick_time
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
        self.thread = Thread(name=self.__str__(), target=self.loop)
        self.thread.start()

    def __del__(self):
        # save weights and trade_history to google sheet
        return None

    def loop(self):
        while True:
            self.tick()
            time.sleep(tick_time)
										
    def tick(self):
        log.info('saving data to disk')
        header_weights = ['bollinger_band_agent', 'bollinger_band_trend_agent', 'fuzzy_logic_agent',
                          'deep_evolution_agent', 'Q_learning_double_duel_recurrent_agent']
        header = ['timestamp', 'symbol', 'action', 'client_order_id', 'order_status', 'bollinger_band_agent', 'bollinger_band_trend_agent', 'fuzzy_logic_agent', 'deep_evolution_agent', 'Q_learning_double_duel_recurrent_agent','open_price', 'close_price', 'quantity', 'profit/loss',  'stoploss', 'takeprofit']
        self.trade_history = self.trade_history[header]
        
        # write to both local database and Google Sheets
        if (os.path.isfile('./local_db/pnl_data/PnL_report.csv')):
            #self.google_api_object.write_google_sheets(self.gs_name_pnl,self.trade_history)
            self.google_api_object.write_pnl_google_sheets(self.trade_history)
            self.trade_history.to_csv('./local_db/pnl_data/PnL_report.csv',index=False)
        else:
            #self.google_api_object.create_google_sheets(self.gs_name_pnl)
            #self.google_api_object.write_google_sheets(self.gs_name_pnl, self.trade_history)
            self.google_api_object.write_pnl_google_sheets(self.trade_history)
            self.trade_history.to_csv('./local_db/pnl_data/PnL_report.csv',index=False)

        if (os.path.isfile('./local_db/knowledge_data/agent_weights.csv')):
            df_agent_weights = pd.DataFrame.from_dict(self.agent_weights)
            df_agent_weights['action'] = df_agent_weights.index
            df_agent_weights.reset_index(inplace=True, drop=True)
            df_agent_weights.to_csv('./local_db/knowledge_data/agent_weights.csv')
            #self.google_api_object.write_google_sheets(self.gs_name_weights, df_agent_weights)
            self.google_api_object.write_agent_weights_google_sheets(df_agent_weights)
        else:
            self.google_api_object.create_google_sheets(self.gs_name_weights)
            df_agent_weights = pd.DataFrame.from_dict(self.agent_weights)
            df_agent_weights['action'] = df_agent_weights.index
            df_agent_weights.reset_index(inplace=True, drop=True)
            df_agent_weights.to_csv('./local_db/knowledge_data/agent_weights.csv')
            #self.google_api_object.write_google_sheets(self.gs_name_weights, df_agent_weights)
            self.google_api_object.write_agent_weights_google_sheets(df_agent_weights)

    def get_weight(self, agent, signal):
        # return the weight of an agent

        return self.agent_weights[agent][signal]


    def update_weight(self, agent, weight):
        # update the weight of an agent
        log.info('updating weight %s', weight)
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
            return self.trade_history[(self.trade_history['profit/loss'].isnull()) & (self.trade_history['order_status']=='closed')]

    def get_unfilled_trades(self):
        if len(self.trade_history) == 0:
            return self.trade_history
        else:
            return self.trade_history[self.trade_history['order_status']!='closed']

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

    def update_order_status(self,index,new_status):
        self.lock.acquire()
        self.trade_history.at[index,'order_status']=new_status
        self.lock.release()

    def dump(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns',None)
        log.info(self.trade_history.head())
        log.info(self.agent_weights)

    def __str__(self):
        return 'knowledge_database'
