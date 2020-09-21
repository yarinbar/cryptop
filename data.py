from settings import *
import ta
from pandas import Series
import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib
from math import pi
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import mpl_finance  # import candlestick_ohlc
from binance import client
from bokeh.plotting import figure, show, output_file
import time

binance_client = client.Client(environ.get('BINANCE_API_KEY'), environ.get('BINANCE_API_SECRET'))

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


class Data:

    def __init__(self, pair, interval):
        self.pair = pair
        self.symbol = binance_coins[pair]
        self.interval = interval

        try:
            self.df = pd.read_csv(r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\data\{}_{}.csv'.format(self.pair,
                                                                                                                    self.interval), index_col=0)
            self.update_dataset()
            self.do_ta()

        except FileNotFoundError:
            self.create_df()

    def create_df(self):
        data = binance_client.get_historical_klines_generator(symbol=self.pair,
                                                              interval=self.interval,
                                                              start_str="1000 day ago UTC")

        candles = []

        for kline in data:
            del kline[-1]
            candles.append(kline)

        df = pd.DataFrame(data=candles, columns=['open_timestamp',
                                                 'open',
                                                 'high',
                                                 'low',
                                                 'close',
                                                 'volume',
                                                 'close_timestamp',
                                                 'quote_asset_volume',
                                                 'taker_base_volume',
                                                 'taker_quote_volume',
                                                 'num_of_trades'])

        self.df = df
        self.do_ta()
        self.save_to_csv()

    def save_to_csv(self):
        try:
            self.df.to_csv(r'YOUR_PATH\data\{}_{}.csv'.format(self.pair, self.interval), header=True)
        except Exception as e:
            print(e)

    def update_dataset(self):

        last_timestamp = self.df['open_timestamp'].values[-1]
        next_candle = self.df['close_timestamp'].values[-1] + 1
        now = binance_client.get_server_time()['serverTime']
        delta = now - last_timestamp
        candles_missed = int(delta / interval_milli[self.interval])

        if candles_missed < 1:
            return

        if candles_missed >= 1:
            data = binance_client.get_historical_klines_generator(symbol=self.pair,
                                                                  interval=self.interval,
                                                                  start_str=int(next_candle))
            candles = []

            for kline in data:
                del kline[-1]
                candles.append(kline)

            df2 = pd.DataFrame(data=candles, columns=['open_timestamp',
                                                      'open',
                                                      'high',
                                                      'low',
                                                      'close',
                                                      'volume',
                                                      'close_timestamp',
                                                      'quote_asset_volume',
                                                      'taker_base_volume',
                                                      'taker_quote_volume',
                                                      'num_of_trades'])

            new = self.df.append(df2, ignore_index=True, sort=True)
            self.df = new
            self.do_ta()
            self.save_to_csv()

    def do_ta(self):

        open = Series(self.df['open'].values).astype('float64')
        high = Series(self.df['high'].values).astype('float64')
        low = Series(self.df['low'].values).astype('float64')
        close = Series(self.df['close'].values).astype('float64')

        print(self.interval)

        #      Trend
        # ----------------
        ema30 = ta.ema(series=close, periods=30)
        ema50 = ta.ema(series=close, periods=50)
        ema100 = ta.ema(series=close, periods=100)
        ema200 = ta.ema(series=close, periods=200)
        macd_diff = ta.macd_diff(close=close, n_fast=12, n_slow=26, n_sign=9)
        macd_signal = ta.macd_signal(close=close, n_fast=12, n_slow=26, n_sign=9)

        self.df['ema30'] = ema30
        self.df['ema50'] = ema50
        self.df['ema100'] = ema100
        self.df['ema200'] = ema200
        self.df['macd_diff'] = macd_diff
        self.df['macd_signal'] = macd_signal

        #     Momentum
        # ----------------
        rsi = ta.rsi(close=close)
        stochastic = ta.stoch(high=high, low=low, close=close)

        self.df['rsi'] = rsi
        self.df['stochastic'] = stochastic

        #    Volatility
        # ----------------
        bollinger_h = ta.bollinger_hband(close=close)
        bollinger_l = ta.bollinger_lband(close=close)
        bollinger_h_indicator = ta.bollinger_hband_indicator(close=close)
        bollinger_l_indicator = ta.bollinger_lband_indicator(close=close)

        self.df['bollinger_h'] = bollinger_h
        self.df['bollinger_l'] = bollinger_l
        self.df['bollinger_h_indicator'] = bollinger_h_indicator
        self.df['bollinger_l_indicator'] = bollinger_l_indicator

        self.save_to_csv()

    def get_next_candle(self):
        return self.df['close_timestamp'].values[-1] + 1

    def plot(self):

        ohlcv = self.df[['open_timestamp', 'open', 'high', 'low', 'close']].tail(1000).values

        ema30 = self.df[['ema30']].tail(1000).values
        ema100 = self.df[['ema100']].tail(1000).values
        bollinger_h = self.df[['bollinger_h']].tail(1000).values
        bollinger_l = self.df[['bollinger_l']].tail(1000).values
        dates = self.df[['open_timestamp']].tail(1000).values

        fig, ax = plt.subplots()
        mpl_finance.candlestick_ochl(ax, ohlcv, width=0.1, colorup='g', alpha=1)
        plt.plot(dates, ema30)
        plt.plot(dates, ema100)
        plt.plot(dates, bollinger_h)
        plt.plot(dates, bollinger_l)

        plt.show()

    def normalize(self, columns=[]):
        """
        :param params: dictionary with string name of columns as key and normalization function as value
        :return: saves updated csv
        """

        if columns == []:
            return

        for column_name in columns:

            array = self.df[column_name].values.reshape(len(self.df[column_name]), 1)
            print(array.shape)
            try:
                isNaN = np.isnan(array)
                array[isNaN] = 0
            except:
                pass

            normed = preprocessing.normalize(array)

            scaler = preprocessing.StandardScaler().fit(array)

            x_scalar = scaler.fit_transform(array)

            self.df['n_' + str(column_name)] = normed
            self.df['s_' + str(column_name)] = x_scalar

            print(x_scalar)
            print(normed)

        self.df['s_rsi'].plot.hist(bins=300, alpha=0.4)
        plt.show()
        self.save_to_csv()


class Candle:
    def __init__(self, timestamp, open, close, high, low, volume, interval):
        self.info = {'timestamp': timestamp,
                     'open': open,
                     'close': close,
                     'high': high,
                     'low': low,
                     'volume': volume,
                     'interval': interval}

    def add_info(self, label, info):
        self.info[label] = info

    def __str__(self):
        msg = ''
        for key, value in self.info.items():
            msg += '{:25}'.format(str(key)) + '{:>25}'.format(str(value)) + '\n'

        msg += '\n'
        return msg
