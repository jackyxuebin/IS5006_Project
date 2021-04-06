from threading import Thread,Lock
from multiagents.broker_agent import BrokerAgent
from app.constants.constants import *
import numpy as np
import time
import logging
log = logging.getLogger('bollinger_band_agent')

class BollingerBandAgent():

    def __init__(self):
        # Lock to prevent other agents from reading signals when tick is in progress
        self.lock = Lock()
        self.signals = []
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.tick()
            time.sleep(tick_time)


    def tick(self):
        self.lock.acquire()
        df = BrokerAgent.get_ohlcv_data(trading_symbol,timeframe)
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['low_band_20'] = df['ma_20'] - df['std_20'] * 2
        df['high_band_20'] = df['ma_20'] + df['std_20'] * 2
        df['over_buy'] = np.where(df['close'] > df['high_band_20'], 1, 0)
        df['sell_signal'] = df['over_buy'].diff()
        df['ma_50'] = df['close'].rolling(window=50).mean()
        df['over_sell'] = np.where(df['close'] < df['low_band_20'], 1, 0)
        df['buy_signal'] = df['over_sell'].diff()
        df['std_50'] = df['close'].rolling(window=50).std()
        df['low_band_50'] = df['ma_50'] - df['std_50'] * 2
        df['high_band_50'] = df['ma_50'] + df['std_50'] * 2
        df['lower'] = abs(df['low_band_20'] - df['low_band_50'])
        df['upper'] = abs(df['high_band_20'] - df['high_band_50'])
        df['trend'] = (df['lower'] - df['upper']) / df['ma_20']
        if df.iloc[-1]['buy_signal']==-1:
            self.signals.append(1)
        elif df.iloc[-1]['sell_signal']==-1:
            self.signals.append(-1)
        else:
            self.signals.append(0)

        log.info('signals %s',self.signals)
        self.lock.release()


    def peek(self):
        self.lock.acquire()
        signal = 0
        if len(self.signals)>0:
            signal = self.signals[-1]
        self.lock.release()
        return signal


    def __str__(self):
        return 'bollinger_band_agent'

