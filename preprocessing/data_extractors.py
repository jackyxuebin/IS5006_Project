from Historic_Crypto import HistoricalData
import pandas as pd
import ccxt
import calendar
from datetime import datetime, date, timedelta
import numpy as np
import time

## Get dataset from CoinBase
# ochlv_df = HistoricalData('BTC-USD',300,'2017-04-02-00-00', '2021-04-02-00-00').retrieve_data()
# ochlv_df.to_csv('bitcoin_train_dataset_2009_2021.csv')

## Fetch OHLCV efficiently with specific timeframe
## Sources: https://techflare.blog/how-to-get-ohlcv-data-for-your-exchange-with-ccxt-library/
hitbtc = ccxt.hitbtc()

def min_ohlcv(dt, pair, limit):
    # UTC native object
    since = calendar.timegm(dt.utctimetuple())*1000
    ohlcv1 = binance.fetch_ohlcv(symbol=pair, timeframe='1m', since=since, limit=limit)
    ohlcv2 = binance.fetch_ohlcv(symbol=pair, timeframe='1m', since=since, limit=limit)
    ohlcv = ohlcv1 + ohlcv2
    return ohlcv

def ohlcv(dt, pair, period='1d'):
    ohlcv = []
    
    limit = 1000
    if period == '1m':
        limit = 720
    elif period == '1d':
        limit = 365
    elif period == '1h':
        limit = 24
    elif period == '5m':
        limit = 288
    for i in dt:

        # it's in GMT/UTC
        # since = calendar.timegm(start_dt.utctimetuple())*1000
        
        # it's in local time
        start_dt = datetime.strptime(i, "%Y%m%d")
        since = int(time.mktime(start_dt.utctimetuple())*1000)
        
        if period == '1m':
            ohlcv.extend(min_ohlcv(start_dt, pair, limit))
        else:
            ohlcv.extend(hitbtc.fetch_ohlcv(symbol=pair, timeframe=period, since=since, limit=limit))
            
    df = pd.DataFrame(ohlcv, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = [datetime.fromtimestamp(float(time)/1000) for time in df['time']]
    df['open'] = df['open'].astype(np.float64)
    df['high'] = df['high'].astype(np.float64)
    df['low'] = df['low'].astype(np.float64)
    df['close'] = df['close'].astype(np.float64)
    df['volume'] = df['volume'].astype(np.float64)
    df.set_index('time', inplace=True)
    return df


# Change both the start day and end day (range)
start_day = "20190402"
start_dt = datetime.strptime(start_day, "%Y%m%d")

end_day = "20210402"
end_dt = datetime.strptime(end_day, "%Y%m%d")

days_num = (end_dt - start_dt).days + 1
datelist = [start_dt + timedelta(days=x) for x in range(days_num)]
datelist = [date.strftime("%Y%m%d") for date in datelist]

df = ohlcv(datelist, 'BTC/USDT', '5m')

# 5 minute BTC/USDT ohlcv data between Jan 2014 and Jan 2019 from crypto exchange
df.to_csv('../local_db/data/bitcoin_train_dataset_2019_2021.csv')
