from broker_agent import BrokerAgent
from constants import currency
from constants import debug
import numpy as np

class ceo:

    def __init__(self, knowledgeDatabase):
        self.knowledgeDatabase = knowledgeDatabase

    def review(self, entry):
        pair = entry['symbol'].split('/')
        if entry['action'] == 1: #buy
            balance = BrokerAgent.get_balance(currency)
            cost = BrokerAgent.get_ticker_price(entry['symbol']) * entry['quantity']
            if float(balance) >= cost:
                print('Buying {} {}'.format(entry['quantity'], entry['symbol']))
                price = BrokerAgent.place_market_buy_order(entry['symbol'], entry['quantity'])
                entry['price'] = price
                entry['stoploss'] = price - entry['stoploss']
                entry['takeprofit'] = price + entry['takeprofit']
                entry['profit/loss'] = np.nan
                self.knowledgeDatabase.record_trade(entry)
            else:
                print('{} not enough balance {}, cost {}'.format(currency,balance,cost))
        elif entry['action'] == -1: #sell
            balance = BrokerAgent.get_balance(pair[0])
            if float(balance) >= entry['quantity']:
                print('Selling {} {}'.format(entry['quantity'], entry['symbol']))
                price = BrokerAgent.place_market_sell_order(entry['symbol'], entry['quantity'])
                entry['price'] = price
                entry['stoploss'] = price + entry['stoploss']
                entry['takeprofit'] = price - entry['takeprofit']
                entry['profit/loss']= np.nan
                self.knowledgeDatabase.record_trade(entry)
            else:
                print('{} not enough balance {}, cost {}'.format (pair[0], balance, entry['quantity']))
        else:
            print('No action')

        if debug:
           self.knowledgeDatabase.dump()