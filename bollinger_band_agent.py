from threading import Lock
from broker_agent import BrokerAgent
from constants import trading_symbol
from constants import timeframe
from constants import tick_time
import numpy as np
import time

class BollingerBandAgent():
    # Lock to prevent other agents from reading signals when tick is in progress
    lock = Lock()
    signals = []

    @staticmethod
    def loop():
        for i in range(60):
            BollingerBandAgent.tick()
            time.sleep(tick_time)

    @staticmethod
    def tick():
        BollingerBandAgent.lock.acquire()
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
            BollingerBandAgent.signals.append(1)
        elif df.iloc[-1]['sell_signal']==-1:
            BollingerBandAgent.signals.append(-1)
        else:
            BollingerBandAgent.signals.append(0)
        #print(df.tail(5)[['over_sell','buy_signal','over_buy','sell_signal','trend']])
        #print(BollingerBandAgent.signals)
        BollingerBandAgent.lock.release()

    @staticmethod
    def peek():
        BollingerBandAgent.lock.acquire()
        signal = 0
        if len(BollingerBandAgent.signals)>0:
            signal = BollingerBandAgent.signals[-1]
        BollingerBandAgent.lock.release()
        return signal

