import numpy as np
import pandas as pd
import sys
from stockstats import StockDataFrame as Sdf
from mas_config import *
import datetime

## This module is a standalone module, you may need to run it separately from our MAS system
def load_dataset(*, file_path: str) -> pd.DataFrame:
    """
    load csv dataset from path
    :return: (df) pandas dataframe
    """
    _data = pd.read_csv(file_path)
    _data['tic'] = 'BTC/USDT'
    return _data

def data_split(df,start,end):
    """
    split the dataset into training or testing using date
    :param data: (df) pandas dataframe, start, end
    :return: (df) pandas dataframe
    """
    data = df[(df.time >= start) & (df.time < end)]
    data=data.sort_values(['time','tic'],ignore_index=True)
    #data  = data[final_columns]
    data.index = data.datadate.factorize()[0]
    return data

def add_technical_indicator(df):
    """
    calcualte technical indicators
    use stockstats package to add technical inidactors
    :param data: (df) pandas dataframe
    :return: (df) pandas dataframe
    """
    cyptocurrency = Sdf.retype(df.copy())
    unique_ticker = cyptocurrency.tic.unique()

    macd = pd.DataFrame()
    rsi = pd.DataFrame()
    cci = pd.DataFrame()
    dx = pd.DataFrame()

    #temp = stock[stock.tic == unique_ticker[0]]['macd']
    for i in range(len(unique_ticker)):
        ## macd
        temp_macd = cyptocurrency[cyptocurrency.tic == unique_ticker[i]]['macd']
        temp_macd = pd.DataFrame(temp_macd)
        macd = macd.append(temp_macd, ignore_index=True)
        ## rsi
        temp_rsi = cyptocurrency[cyptocurrency.tic == unique_ticker[i]]['rsi_30']
        temp_rsi = pd.DataFrame(temp_rsi)
        rsi = rsi.append(temp_rsi, ignore_index=True)
        ## cci
        temp_cci = cyptocurrency[cyptocurrency.tic == unique_ticker[i]]['cci_30']
        temp_cci = pd.DataFrame(temp_cci)
        cci = cci.append(temp_cci, ignore_index=True)
        ## adx
        temp_dx = cyptocurrency[cyptocurrency.tic == unique_ticker[i]]['dx_30']
        temp_dx = pd.DataFrame(temp_dx)
        dx = dx.append(temp_dx, ignore_index=True)


    df['macd'] = macd
    df['rsi'] = rsi
    df['cci'] = cci
    df['adx'] = dx

    return df


def preprocess_data():
    """data preprocessing pipeline"""

    df = load_dataset(file_path=TRAINING_DATA_FILE)
    
    # get data after 2009
    df = df[df.time>="2014-01-02 00:00:00"]
    
    # add technical indicators using stockstats
    df_final=add_technical_indicator(df)
    
    # fill the missing values at the beginning
    df_final.fillna(method='bfill',inplace=True)
    
    return df_final

def add_turbulence(df):
    """
    add turbulence index from a precalcualted dataframe
    :param data: (df) pandas dataframe
    :return: (df) pandas dataframe
    """
    turbulence_index = calcualte_turbulence(df)
    df = df.merge(turbulence_index, on='time')
    df = df.sort_values(['time','tic']).reset_index(drop=True)
    return df

def calcualte_turbulence(df):
    """calculate turbulence index based on dow 30"""
    # can add other market assets
    print('yes')
    print(df[df['time'].duplicated()])


    df_price_pivot=df.reset_index().pivot(index='time', columns='tic', values='close')
    unique_date = df.datadate.unique()
    print('yexs')
    # start after a year
    start = 252
    turbulence_index = [0]*start
    #turbulence_index = [0]
    count=0
    for i in range(start,len(unique_date)):
        current_price = df_price_pivot[df_price_pivot.index == unique_date[i]]
        hist_price = df_price_pivot[[n in unique_date[0:i] for n in df_price_pivot.index ]]
        cov_temp = hist_price.cov()
        current_temp=(current_price - np.mean(hist_price,axis=0))
        temp = current_temp.values.dot(np.linalg.inv(cov_temp)).dot(current_temp.values.T)
        if temp>0:
            count+=1
            if count>2:
                turbulence_temp = temp[0][0]
            else:
                #avoid large outlier because of the calculation just begins
                turbulence_temp=0
        else:
            turbulence_temp=0
        turbulence_index.append(turbulence_temp)
    
    
    turbulence_index = pd.DataFrame({'time':df_price_pivot.index,
                                     'turbulence':turbulence_index})
    return turbulence_index




# df_final = pd.read_csv('../local_db/data/preprocessed_data.csv', index_col=0)
# df_final.to_csv('../local_db/data/preprocessed_data.csv')




