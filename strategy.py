from settings import *


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

        self.old_signal_methods = []
        self.__wrong = 0
        self.__right = 0

    def signal(self, data):
        return self.signal_method(data=data)

    def update_signal(self, new_signal_method):
        self.old_signal_methods.append(self.signal_method)
        self.signal_method = new_signal_method

    def wrong_call(self):
        self.__wrong += 1

    def right_call(self):
        self.__right += 1

    def get_accuracy(self):
        try:
            accuracy = 100 * (self.__right / (self.__right + self.__wrong))
        except ZeroDivisionError:
            return 0

        return accuracy


