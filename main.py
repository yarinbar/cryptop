
from settings import *
from data import Data
import time
import ccxt
import random
from position import Long, Short
import numpy as np
import pickle
from random import uniform
import os
from pandas import Series
import pandas as pd
from strategy import Strategy
import dataset
import keras

client_intervals = {'1m': KLINE_INTERVAL_1MINUTE,
                    '5m': KLINE_INTERVAL_5MINUTE,
                    '15m': KLINE_INTERVAL_15MINUTE,
                    '30m': KLINE_INTERVAL_30MINUTE,
                    '1h': KLINE_INTERVAL_1HOUR,
                    '2h': KLINE_INTERVAL_2HOUR,
                    '4h': KLINE_INTERVAL_4HOUR,
                    '6h': KLINE_INTERVAL_6HOUR,
                    '12h': KLINE_INTERVAL_12HOUR,
                    '1d': KLINE_INTERVAL_1DAY,
                    '3d': KLINE_INTERVAL_3DAY,
                    '1w': KLINE_INTERVAL_1WEEK}
binance_class = getattr(ccxt, 'binance')
binance = binance_class({
    'apiKey': environ.get('BINANCE_API_KEY'),
    'secret': environ.get('BINANCE_API_SECRET'),
    'timeout': 3000,
    'enableRateLimit': True,
    'adjustForTimeDifference': True
})

candles = {'rsi': 0, 'macd': 0, 'volume': 0}

def mean_deviation(dataset):

    dataset = dataset.tail(5)

    rsi         = np.array(dataset['rsi'].values)
    bol_ind_h   = np.array(dataset['bollinger_h_indicator'].values)
    bol_ind_l   = np.array(dataset['bollinger_l_indicator'].values)
    stoch       = np.array(dataset['stochastic'].values)

    if np.where(rsi > 80)[0].shape[0] > 3 and np.where(bol_ind_h == 1)[0].shape[0] > 3 and np.where(stoch > 80)[0].shape[0] > 3:
        return -1

    if np.where(rsi < 20)[0].shape[0] > 3 and np.where(bol_ind_l == 1)[0].shape[0] > 3 and np.where(stoch < 20)[0].shape[0] > 3:
        return 1
    return 0


if __name__ == '__main__':

    params = ['bollinger_l_indicator',
              'bollinger_h_indicator',
              'rsi',
              'stochastic',
              'volume',
              'last_candle_change',
              'macd_signal',
              'num_of_trades']


    ds = Data("ETHUSDT", '2h')
    dataset.create_new_dataset(ds, params)

    X_train, y_train, X_test, y_test = dataset.load_dataset([r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\btcusdt\1h',
                                                             r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\ethusdt\1h',
                                                             r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\ltcusdt\1h',
                                                             r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\bnbusdt\1h',
                                                             r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\xrpusdt\1h'])

    print("X_train.shape:     {}".format(X_train.shape))
    print("y_train.shape:     {}".format(y_train.shape))
    print("X_test.shape:      {}".format(X_test.shape))
    print("y_test.shape:      {}".format(y_test.shape))


