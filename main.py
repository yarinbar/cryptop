from settings import *
from data import Data
import time
import tensorflow as tf
from tensorflow import keras
from tensorflow import layers
import ccxt
import random
from position import Long, Short
import numpy as np

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


def position_unit_test():
    p1 = Long(pair='ETHUSDT')
    p2 = Short(pair='ETHBTC')

    test_dict = {'test': True}

    # should do nothing
    p1.update()
    p2.update()

    assert p1.status == EMPTY and p2.status == EMPTY

    # should fail
    assert p1.close(params=test_dict) == -1
    assert p2.close(params=test_dict) == -1

    # should fail because long target >= limit
    assert p1.open_limit(amount=1, limit=230, target_price=200, stop_loss=190, params=test_dict) == -1

    # should fail because short limit >= target
    assert p2.open_limit(amount=1, limit=210, target_price=220, stop_loss=190, params=test_dict) == -1

    # succeed
    assert p1.open_limit(amount=1, limit=230, target_price=250, stop_loss=190, params=test_dict) == 0
    assert p2.open_limit(amount=1, limit=200, target_price=190, stop_loss=250, params=test_dict) == 0

    while p1.status != OPEN or p2.status != OPEN:
        p1.update()
        p2.update()

    assert p1.is_secured
    assert p2.is_secured

    assert p1['open']['status'] == 'closed'
    assert p2['open']['status'] == 'closed'

    assert p1.expose() == 0
    assert p2.expose() == 0

    assert not p1.is_secured
    assert not p2.is_secured

    # p1 open price = 230
    # p2 open price = 200
    # should fail because stoploss is bigger than open price
    assert p1.secure(stop_loss=231, target_price=250, params=test_dict) == -1
    assert p2.secure(stop_loss=220, target_price=212, params=test_dict) == -1

    assert p1.secure(stop_loss=225, target_price=235, params=test_dict) == 0
    assert p2.secure(stop_loss=205, target_price=195, params=test_dict) == 0

    assert p1.is_secured and p2.is_secured

    assert p1.close(price=240, params=test_dict) == 0
    assert p2.close(price=400, params=test_dict) == 0

    test_dict['price'] = 230

    assert p1.open_market(amount=1, target_price=220, stop_loss=220, params=test_dict) == -1
    assert p2.open_market(amount=1, target_price=220, stop_loss=220, params=test_dict) == -1

    assert p1.open_market(amount=1, target_price=240, stop_loss=290, params=test_dict) == -1
    assert p2.open_market(amount=1, target_price=240, stop_loss=220, params=test_dict) == -1

    assert p1.get_profit() == 10 - p1.get_fee()
    assert p2.get_profit() == - 1 / 2

    assert 4.1 <= p1.get_profit_percent() <= 4.15
    assert p2.get_profit_percent() == -50

    assert p2.get_profit_percent(current_price=50) == -50

    assert p1['stop_loss'] is None and p1['take_profit'] is None
    assert p2['stop_loss'] is None and p2['take_profit'] is None

candles = {'rsi': 0, 'macd': 0, 'volume': 0}

def build_model():
    model = keras.Sequential([layers.Dense(64, activation=tf.nn.relu, input_shape=[len(candles) * 10]),
                              layers.Dense(64, activation=tf.nn.relu),
                              layers.Dense(1)])

def move_to(key, src, dest):
    if type(src) != dict or type(dest) != dict:
        return -1

    try:
        tmp = src[key]
        del src[key]
        dest[key] = tmp
    except Exception as e:
        pass

    return 0

def get_size(dict1):

    sum = 0
    for key, booklet in dict1.items():
        sum += len(booklet)

    return sum


class A:
    def __init__(self, d):
        self.p = d['p']
        self.d = d

if __name__ == '__main__':
    #print(binance.has)
    open_orders= [1,2,3,4,5,6]
    # hist = np.zeros((len(open_orders)))
    # order_hist = np.copy(open_orders)
    # order_hist = np.append(order_hist, hist)
    # order_hist = order_hist.reshape((2, len(open_orders)))
    #
    # i, j = np.where(order_hist == 6)
    # print(i[0], j[0])

    # dict1 = {'yarin': {1: 2, 2: 3},
    #          'gal': {1: 2, 2: 3},
    #          'eden': {1: 2, 2: 3}}
    #
    # print(get_size(dict1))

    d = {'p': 'lol'}
    a = A(d=d)
    d['p'] = 'sad'
    b = A(d=d)
    print(a.p, a.d)
    print(b.p, b.d)







