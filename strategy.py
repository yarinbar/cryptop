from data import Data


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

    def signal(self, current_ticker, dataset=None):

        if type(current_ticker) is not dict:
            raise ValueError("ticker should be dictionary type")

        if dataset is not None and not isinstance(dataset, Data):
            raise ValueError("dataset should be Data type")

        signal = self.signal_method(current_ticker, dataset)

        return self.cooldown_method(signal)

    def get_accuracy(self):

        if self._right_calls == 0 and self._wrong_calls == 0:
            return 50

        if self._right_calls == 0:
            return 0

        if self._wrong_calls == 0:
            return 100

        return 100 * (self._right_calls / (self._right_calls + self._wrong_calls))

    def wrong_call(self):
        self._wrong_calls += 1

    def right_call(self):
        self._right_calls += 1

    def _signal_handler(self):
        pass




