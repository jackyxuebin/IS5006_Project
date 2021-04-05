from threading import Thread
from constants import trading_symbol
from constants import pnl_time
from broker_agent import BrokerAgent
import time
import logging
log = logging.getLogger('pnl_agent')

class pnlAgent():

    def __init__(self, knowledgeDatabase):
        self.knowledgeDatabase = knowledgeDatabase
        self.thread = Thread(name=self.__str__(), target=self.loop)
        self.thread.start()


    def loop(self):
        while True:
            self.tick()
            time.sleep(pnl_time)

    def tick(self):
        # scans knowledge database for any violation of stoploss and take profit condition
        log.info('ticking in PNL agent')
        to_monitor = self.knowledgeDatabase.get_open_trades()
        log.info(to_monitor.head())
        current_price = BrokerAgent.get_ticker_price(trading_symbol)
        for index, row in to_monitor.iterrows():
            if row['action'] == 1: # buy order
                if current_price < row['stoploss'] or current_price > row['takeprofit']: # risk condition triggered
                    closing_price = BrokerAgent.place_market_sell_order(trading_symbol,row['quantity'])
                    self.knowledgeDatabase.update_pnl(index, closing_price, row['quantity']*(closing_price - row['open_price']))
                    log.info('closing buy position')
            elif row['action'] == -1: # sell order
                if current_price > row['stoploss']  or current_price < row['takeprofit']: # risk condition triggered
                    closing_price = BrokerAgent.place_market_buy_order(trading_symbol,row['quantity'])
                    self.knowledgeDatabase.update_pnl(index, closing_price, row['quantity']*(row['open_price'] - closing_price))
                    log.info('closing sell position')


    def __str__(self):
        return 'pnlAgent'