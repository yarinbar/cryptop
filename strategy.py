import backtrader as bt


class MeanRev(bt.Strategy):
    def __init__(self):

        self.macd = bt.indicators.MACD()

    def next(self):
        if self.macd > 15:
            self.buy()
