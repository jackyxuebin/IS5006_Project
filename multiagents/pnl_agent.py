from threading import Thread
from app.constants.constants import *
from multiagents.broker_agent import BrokerAgent
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
        # updates order status for unfilled order
        unfilled_trades = self.knowledgeDatabase.get_unfilled_trades()
        log.info('unfilled trades %s',unfilled_trades)
        for index, row in unfilled_trades.iterrows():
            new_status = BrokerAgent.get_order_status(row['client_order_id'],row['symbol'])
            self.knowledgeDatabase.update_order_status(index,new_status)
            log.info('updated order %s with status %s',row['client_order_id'],new_status)

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
