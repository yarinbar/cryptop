from book import PositionBook
import numpy as np
import random
import pandas as pd
from config import *
from strategy import Strategy
import time
import ccxt
import pickle
import os
import string
from data import Data



binance_class = getattr(ccxt, 'binance')
binance = binance_class({
    'apiKey': environ.get('BINANCE_API_KEY'),
    'secret': environ.get('BINANCE_API_SECRET'),
    'timeout': 3000,
    'enableRateLimit': True,
    'adjustForTimeDifference': True
})

class Bot(object):

    @staticmethod
    def allowed_allowance(base, quote, asked_allowance):

        existing_balances = binance.fetch_balance()

        approved_allowance = {base:  0,
                              quote: 0}


        if asked_allowance is None:
            return approved_allowance

        if base in asked_allowance and base in existing_balances[base]:
            approved_allowance[base] = min(existing_balances[base]['free'], asked_allowance[base])

        if quote in asked_allowance and quote in existing_balances[quote]:
            approved_allowance[quote] = min(existing_balances[quote]['free'], asked_allowance[quote])


        return approved_allowance


    def __init__(self, **kwargs):

        self.name = kwargs.get('name', ''.join(random.choices(string.ascii_lowercase, k=6)))

        if 'name' not in kwargs or type(kwargs['name']) is not str or len(kwargs['name']) < 3:
            raise ValueError("name must be a 3 or more long string")

        self.strategy           = kwargs.get('strategy', None)
        self.pair               = kwargs.get('pair', None)
        self.allowance          = self.allowed_allowance(base=self.base,
                                                         quote=self.quote,
                                                         asked_allowance=kwargs.get('allowance', None))
        self.avail_allowance    = self.allowance.copy()
        self._last_buy          = None
        self._last_sell         = None
        self.interval           = kwargs.get('interval', None)

        if not isinstance(self.strategy, Strategy):
            raise ValueError("strategy must be a Strategy instance")

        if self.pair is None or kwargs['pair'] not in binance_coins:
            raise ValueError("this pair is not a valid pair")

        if self.interval is None or self.interval not in interval_milli:
            raise ValueError("please provide a valid interval")

        self.symbol     = binance_coins[self.pair]
        self.base       = self.symbol.split('/')[0]
        self.quote      = self.symbol.split('/')[1]

        self.data       = Data(pair=self.pair, interval=self.interval)
        self.book       = PositionBook(pair=self.pair)


    def _open(self, params):
        pass

    def _close(self):
        pass

    def _sync(self):
        # syncing position book
        # syncing allowance
        pass

    def _decide(self, **kwargs):

        packet = kwargs.get('packet', None)

        # if total cost < avail allowance - spare open
        if self.avail_allowance[self.base] < 2:
            return False

        return True




    def run(self):

        try:
            next_candle = self.data.get_next_candle()
            while True:

                server_time = binance.fetch_ticker(symbol=self.symbol)['timestamp']

                # next candle occurred
                if next_candle < server_time:

                    self.data.update_dataset()
                    next_candle = self.data.get_next_candle()

                    packet = self.strategy.signal(dataset=self.data)
                    if self._decide(packet=packet):
                        # TODO - last_buy last_sell update etc
                        pass

                self.book.sync()

                time.sleep(interval_secs[self.interval] / UPDATES_FREQ)


        except Exception as e:
            pass

# TODO - make wrapper
"""
    def _backup(self):

        script_dir = os.path.dirname(__file__)
        rel_path = 'bot_backups/{0}_{1}.backup.pickle'.format(self.name, int(time.time()))
        abs_file_path = os.path.join(script_dir, rel_path)

        pickle.dump(self,
                    open(abs_file_path, 'wb'),
                    protocol=pickle.HIGHEST_PROTOCOL)

        folder_path = os.path.dirname(__file__) + '/bot_backups/'
        file_list = os.listdir(folder_path)
        backups = [file_name for file_name in file_list if self.name in file_name]
        backups.sort()

        if len(backups) > 50:
            rel_path = 'bot_backups/{}'.format(backups[0])
            abs_file_path = os.path.join(script_dir, rel_path)
            os.remove(abs_file_path)


    def _restore(self, name):

        script_dir = os.path.dirname(__file__)
        rel_path = 'bot_backups/{}_{}'.format(self.name, int(time.time()))
        abs_backups_path = os.path.join(script_dir, rel_path)
        file_list = os.listdir(abs_backups_path)
        backups = [name for file_name in file_list if name in file_name]

        if len(backups) == 0:
            return False

        backups.sort()

        answer = None

        while type(answer) is not str or (answer.lower() != 'n' and answer.lower() != 'y'):
            answer = input("We've detected previous versions of the bot, would you like to restore it? Y / N")

        if answer.lower() == 'n':
            return False

        



"""










