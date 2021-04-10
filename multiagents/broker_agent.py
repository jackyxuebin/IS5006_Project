import ccxt
import datetime
import pandas as pd
from app.constants.constants import *
from matplotlib import pyplot as plt
import logging
log = logging.getLogger('broker_agent')

class BrokerAgent():

    hitbtc = ccxt.hitbtc({'apiKey': api_key,
                          'secret': secret,
                          'urls': {
                              'api': {
                                  'private': 'https://api.demo.hitbtc.com'
                              }
                          },
                          'verbose': False})

    @staticmethod
    def get_ohlcv_data(trading_symbol, candlestick_timeframe, limit=100):
        ohlcv = BrokerAgent.hitbtc.fetch_ohlcv(trading_symbol, candlestick_timeframe, limit=limit, params={'sort': 'DESC'})
        df = pd.DataFrame(ohlcv, columns=['Date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = df.Date.apply(lambda x: datetime.datetime.fromtimestamp(x / 1000.0).strftime('%Y-%m-%d %H:%M:%S'))
        df.index = df.set_index('date').index.astype('datetime64[ns]')
        return df

    @staticmethod
    def get_balance(currency):
        balance = BrokerAgent.hitbtc.fetch_balance({'type': 'trading'})
        for k in balance['info']:
           if k['currency'] == currency:
               return k['available']
        return None

    @staticmethod
    def get_ticker_price(trading_symbol):
        ticker = BrokerAgent.hitbtc.fetch_ticker(trading_symbol)
        return ((float)(ticker['info']['bid']) + (float)(ticker['info']['ask']))/2

    @staticmethod
    def place_market_buy_order(trading_symobol, amount):
        res = BrokerAgent.hitbtc.create_market_buy_order(trading_symobol, amount)
        return res['price']


    @staticmethod
    def place_market_sell_order(trading_symobol, amount):
        res = BrokerAgent.hitbtc.create_market_sell_order(trading_symobol, amount)
        return res['price']


    @staticmethod
    def place_limit_buy_order(trading_symbol, amount, price):
        res = BrokerAgent.hitbtc.create_limit_buy_order(trading_symbol, amount, price)
        return res['clientOrderId']

    @staticmethod
    def place_limit_sell_order(trading_symbol, amount, price):
        res = BrokerAgent.hitbtc.create_limit_sell_order(trading_symbol, amount, price)
        return res['clientOrderId']

    @staticmethod
    def get_order_status(clientOrderId, trading_symbol):
        res = BrokerAgent.hitbtc.fetch_order(clientOrderId, trading_symbol)
        return res['status']

    @staticmethod
    def cancel_order(clientOrderId, trading_symbol):
        res = BrokerAgent.hitbtc.cancel_order(clientOrderId,trading_symbol)


