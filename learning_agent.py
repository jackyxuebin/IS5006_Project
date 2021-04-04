import time
from constants import learn_time
from constants import trading_symbol
from constants import debug
from threading import Thread
from broker_agent import BrokerAgent


class learningAgent():
    def __init__(self,  knowledgeDatabase, agents):
        self.agents = agents
        self.knowledgeDatabase = knowledgeDatabase
        self.thread = Thread(name=self.__str__(), target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.tick()
            time.sleep(learn_time)


    def tick(self):
        print('learning agent tick')
        # close all open trades
        open_trades = self.knowledgeDatabase.get_open_trades()
        for index,row in open_trades.iterrows():
            if row['action']==1:
                closing_price = BrokerAgent.place_market_sell_order(trading_symbol, row['quantity'])
                self.knowledgeDatabase.update_pnl(index, closing_price, row['quantity']*(closing_price - row['open_price']))
                print('closing buy position')
            elif row['action']==-1:
                closing_price = BrokerAgent.place_market_buy_order(trading_symbol, row['quantity'])
                self.knowledgeDatabase.update_pnl(index, closing_price, row['quantity']*(row['open_price'] - closing_price))
                print('closing sell position')

        # update weights of agents
        for agent in self.agents:
            long_profit_factor = 0
            short_profit_factor = 0
            new_weight = {0: 0} # neutral signal has 0 weight
            # aggregate profit when signal is buy
            long_profit = self.knowledgeDatabase.get_agg_pnl(agent.__str__(),1,True)
            long_loss = self.knowledgeDatabase.get_agg_pnl(agent.__str__(),1,False)
            print(long_profit,long_loss)
            if long_profit == 0 or long_loss == 0:
                print('not enough data to update weights')
                new_weight[1] = self.knowledgeDatabase.get_weight(agent.__str__(),1)
            else:
                long_profit_factor = long_profit/abs(long_loss)-1
                # reset long profit factor to 0 if less than 0
                if long_profit_factor < 0:
                    long_profit_factor = 0
                new_weight[1] = long_profit_factor

            # aggregate profit when signal is sell
            short_profit = self.knowledgeDatabase.get_agg_pnl(agent.__str__(),-1,True)
            short_loss = self.knowledgeDatabase.get_agg_pnl(agent.__str__(),-1,False)
            print(short_profit,short_loss)
            if short_profit == 0 or short_loss == 0:
                print('not enough data to update weights')
                new_weight[-1] = self.knowledgeDatabase.get_weight(agent.__str__(),-1)
            else:
                short_profit_factor = short_profit/abs(short_loss)-1
                if short_profit_factor < 0:
                    short_profit_factor=0
                new_weight[-1] = short_profit_factor
            # update knowledge database with new weights

            self.knowledgeDatabase.update_weight(agent.__str__(),new_weight)
            self.knowledgeDatabase.dump()

    def __str__(self):
        return 'learning_agent'