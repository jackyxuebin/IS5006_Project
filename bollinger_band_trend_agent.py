from threading import Lock
from broker_agent import BrokerAgent
from constants import trading_symbol
from constants import timeframe
from constants import tick_time
import numpy as np
import time

class BollingerBandTrendAgent():
    # Lock to prevent other agents from reading signals when tick is in progress
    lock = Lock()
    signals = []

    @staticmethod
    def loop():
        for i in range(60):
            BollingerBandTrendAgent.tick()
            time.sleep(tick_time)

    @staticmethod
    def tick():
        BollingerBandTrendAgent.lock.acquire()
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
        BollingerBandTrendAgent.signals.append(df.iloc[-1]['trend'])
        print(BollingerBandTrendAgent.signals)
        BollingerBandTrendAgent.lock.release()

    @staticmethod
    def peek():
        BollingerBandTrendAgent.lock.acquire()
        signal = 0
        if len(BollingerBandTrendAgent.signals)>0:
            signal = BollingerBandTrendAgent.signals[-1]
        BollingerBandTrendAgent.lock.release()
        return signal

