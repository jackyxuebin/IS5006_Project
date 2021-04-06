from multiagents.broker_agent import BrokerAgent
from app.constants.constants import *
import numpy as np
from datetime import datetime
import logging
log = logging.getLogger('ceo')

class ceo:

    def __init__(self, knowledgeDatabase):
        self.knowledgeDatabase = knowledgeDatabase

    def review(self, entry):
        pair = entry['symbol'].split('/')
        if entry['action'] == 1: #buy
            balance = BrokerAgent.get_balance(currency)
            cost = BrokerAgent.get_ticker_price(entry['symbol']) * entry['quantity']
            if float(balance) >= cost:
                log.info('Buying {} {}'.format(entry['quantity'], entry['symbol']))
                price = BrokerAgent.place_market_buy_order(entry['symbol'], entry['quantity'])
                entry['open_price'] = price
                entry['stoploss'] = price - entry['stoploss']
                entry['takeprofit'] = price + entry['takeprofit']
                entry['profit/loss'] = 0
                entry['timestamp'] = datetime.now()
                self.knowledgeDatabase.record_trade(entry)
            else:
                log.info('{} not enough balance {}, cost {}'.format(currency,balance,cost))
        elif entry['action'] == -1: #sell
            balance = BrokerAgent.get_balance(pair[0])
            if float(balance) >= entry['quantity']:
                log.info('Selling {} {}'.format(entry['quantity'], entry['symbol']))
                price = BrokerAgent.place_market_sell_order(entry['symbol'], entry['quantity'])
                entry['open_price'] = price
                entry['stoploss'] = price + entry['stoploss']
                entry['takeprofit'] = price - entry['takeprofit']
                entry['profit/loss']= 0
                entry['timestamp'] = datetime.now()
                self.knowledgeDatabase.record_trade(entry)
            else:
                log.info('{} not enough balance {}, cost {}'.format (pair[0], balance, entry['quantity']))
        else:
            log.info('No action')

        self.knowledgeDatabase.dump()