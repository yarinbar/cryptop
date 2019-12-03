from data import Data
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series
import pandas as pd


class Strategy:

    def __init__(self, name, signal_method):

        if type(name) is not str:
            raise ValueError("strategy name must be a string")

        if len(name) < 3:
            raise ValueError("name must be at least 3 char long")

        if signal_method is None:
            raise ValueError("signal method is a must argument")

        self.name = name.lower()

        self.signal_method = signal_method

        self._right_calls = 0
        self._wrong_calls = 0

    @property
    def accuracy(self):

        if self._right_calls == 0 and self._wrong_calls == 0:
            return 50

        if self._right_calls == 0:
            return 0

        if self._wrong_calls == 0:
            return 100

        return 100 * (self._right_calls / (self._right_calls + self._wrong_calls))

    def signal(self, dataset):

        if dataset is not None and not isinstance(dataset, Data):
            raise ValueError("dataset should be Data type")

        df = dataset.df

        return self.signal_method(df)

    def wrong_call(self):
        self._wrong_calls += 1

    def right_call(self):
        self._right_calls += 1

    def _signal_handler(self):
        pass

    def plot_performance(self, dataset):

        x = Series(dataset.df['close_timestamp'].astype('float64'))
        y = Series(dataset.df['close'].astype('float64'))

        df = dataset.df

        mark_sell = []
        mark_buy  = []

        ds_size = dataset.df_size()

        for i in range(128, ds_size):
            new_df = dataset.head(num=i)
            signal = self.signal_method(new_df)

            # SELL signal
            if signal < -0.95:
                mark_sell.append(i)

            # BUY signal
            if signal > 0.95:
                mark_buy.append(i)

        print(len(mark_buy))
        plt.plot(x, y, '-gD', markevery=mark_buy)
        plt.show()
