from broker_agent import BrokerAgent
from constants import currency

class ceo:

    @staticmethod
    def review(symbol, action, amount, stoploss):
        pair = symbol.split('/')
        if action == 1: #buy
            balance = BrokerAgent.get_balance(currency)
            cost = BrokerAgent.get_ticker_price(symbol) * amount
            if float(balance) >= cost:
                print('Buying {} {}'.format(amount, symbol))
                BrokerAgent.place_market_buy_order(symbol, amount)
            else:
                print('{} not enough balance {}, cost {}'.format(currency,balance,cost))
        elif action == -1: #sell
            balance = BrokerAgent.get_balance(pair[0])
            if float(balance) >= amount:
                print('Selling {} {}'.format(amount, symbol))
                BrokerAgent.place_market_sell_order(symbol, amount)
            else:
                print('{} not enough balance {}, cost {}'.format (pair[0], balance, amount))
        else:
            print('No action')