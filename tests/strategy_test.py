
import unittest
from strategy import Strategy
from random import uniform

def mean_deviation(ticker, dataset):
    return uniform(-1, 1)

class StrategyTest(unittest.TestCase):

    def test_init(self):

        # strategy name should be more than 3 char long
        with self.assertRaises(ValueError):
            strat = Strategy(name="", signal_method=None)

        # strategy name should be a string
        with self.assertRaises(ValueError):
            strat = Strategy(name=5, signal_method=None)

        # signal method is a must
        with self.assertRaises(ValueError):
            strat = Strategy(name="mean deviation", signal_method=None)

        strat = Strategy(name='mean deviation', signal_method=mean_deviation)

    def test_signal(self):

        strat = Strategy(name='mean deviation', signal_method=mean_deviation)

        maximum = -1
        minimal = 1
        for i in range(100000):
            signal = strat.signal(current_ticker={})
            self.assertLess(signal, 1)
            self.assertGreater(signal, -1)

            if signal < minimal:
                minimal = signal

            if signal > maximum:
                maximum = signal

        print(maximum)
        print(minimal)

    def test_accuracy(self):

        strat = Strategy(name='mean deviation', signal_method=mean_deviation)

        self.assertEqual(strat.get_accuracy(), 50)

        strat.right_call()

        self.assertEqual(strat.get_accuracy(), 100)

        for i in range(10000):
            strat.right_call()

        for i in range(5000):
            strat.wrong_call()

        self.assertAlmostEqual(66.67, strat.get_accuracy(), 2)