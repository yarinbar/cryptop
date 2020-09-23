
from data import Data
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series
import pandas as pd



class Strategy:

    def __init__(self, name, signal_method, signal_handler):
        """
        :param name: strategy name str
        :param signal_method: gets candle and params, returns double [-1, 1]
        :param signal_handler: gets bot and signal returns dictionary:

        packet = {"decision":       1           // -1, 0, 1,
                  "price":          ?           // float
                  "amount":         1           // float
                  "target_price":   ?           // float
                  "stop_loss":      ?           // float
                  "date_due":       ??          // date in milliseconds
                  "position":       [??]}       // list of Position type

        """

        self.name = name
        self.signal_method = signal_method
        self.signal_handler = signal_handler

        self._right_calls = 0
        self._wrong_calls = 0



    def update_signal(self, new_signal_method):
        self.old_signal_methods.append(self.signal_method)
        self.signal_method = new_signal_method

    def signal(self, dataset):

        if dataset is not None and not isinstance(dataset, Data):
            raise ValueError("dataset should be Data type")

        df = dataset.df

        return self.signal_method(df)

    def wrong_call(self):
        self.__wrong += 1

    def right_call(self):
        self.__right += 1


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
        
    def get_accuracy(self):
        try:
            accuracy = 100 * (self.__right / (self.__right + self.__wrong))
        except ZeroDivisionError:
            return 0

        return accuracy
