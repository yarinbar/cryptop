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
import random
import matplotlib.pyplot as plt

def determine_y_true(window, current_index):

    good_change  = 6
    bad_change   = 4
    change_limit = 0.5

    close  = np.array(window['close'].values)
    change = np.array(window['last_candle_change'].values)
    rsi    = np.array(window['rsi'].values)

    current_change = float(change[current_index])
    current_close  = float(close[current_index])
    current_rsi    = float(rsi[current_index])

    future = close[current_index:].astype('float32')

    max_close = float(np.amax(future))
    min_close = float(np.amin(future))

    max_change = ((max_close - current_close) / current_close) * 100
    min_change = ((min_close - current_close) / current_close) * 100

    if max_change > good_change and min_change > -bad_change and current_rsi < 30:
        return 1

    if min_change < -good_change and max_change < bad_change and current_rsi > 70:
        return -1

    return 0


def create_dir(pair, interval):

    script_dir = os.path.dirname(__file__)
    rel_path = 'datasets/{}/{}'.format(pair.lower(), interval.lower())
    abs_backups_path = os.path.join(script_dir, rel_path)

    buy_path = os.path.join(abs_backups_path, 'buy')
    hold_path = os.path.join(abs_backups_path, 'hold')
    sell_path = os.path.join(abs_backups_path, 'sell')

    if not os.path.exists(abs_backups_path):
        os.makedirs(abs_backups_path)
        os.makedirs(buy_path)
        os.makedirs(hold_path)
        os.makedirs(sell_path)

def save_to_dir(l, dir):

    for i in range(len(l)):
        path = os.path.join(dir, "{}".format(i + 1))
        np.save(path, l[i])

def selected_point(title, x, y, markevery):

    color = None
    if title == 'buy':
        color = 'green'
    if title == 'sell':
        color = 'red'

    plt.figure()
    plt.plot(x, y, '-kD', markevery=markevery, markerfacecolor=color, markeredgecolor=color)
    plt.show()

    choose = input("1 - choose     2 - skip")

    if choose == 1:
        return True

    return False


def create_matrix(df, cols):

    mat = []

    for col in cols:
        arr = np.array(df[col].values)
        norm = np.linalg.norm(arr, axis=0, keepdims=True)
        if norm != 0:
            arr = arr / norm

        mat.append(arr)

    return np.array(mat).flatten()

def create_new_dataset(data, params, past_size=128, future_size=32):

    print("DATASET: {} {}".format(data.pair.upper(), data.interval.upper()))

    df       = data.df[:-VAL_SIZE]
    pair     = data.pair
    interval = data.interval

    create_dir(pair, interval)

    iterations = 0 if df.shape[0] - past_size - future_size < 0 else df.shape[0] - past_size - future_size

    prices     = np.array(df['close'].values)
    timestamps = np.array(df['close_timestamp'].values)

    buy_i  = []
    hold_i = []
    sell_i = []

    buy  = []
    hold = []
    sell = []

    # for each row
    for i in range(256, iterations):

        past   = df.iloc[i:past_size + i]
        future = df.iloc[past_size + i:past_size + future_size + i]
        window = df.iloc[i:past_size + i + (2 * future_size)]

        matrix = create_matrix(past, params)
        if np.any(np.isnan(matrix)):
            continue

        y_true = determine_y_true(window, past_size)

        if y_true == 1:
            buy_i.append(past_size + i)
            buy.append(matrix)

        if y_true == 0:
            hold_i.append(past_size + i)
            hold.append(matrix)

        if y_true == -1:
            sell_i.append(past_size + i)
            sell.append(matrix)


    # PLOT THE DATASET
    plt.figure()
    plt.title("BUY POINTS")
    plt.plot(timestamps, prices, '-kD', markevery=buy_i, markerfacecolor='green', markeredgecolor='green')
    plt.show()
    plt.figure()
    plt.title("SELL POINTS")
    plt.plot(timestamps, prices, '-kD', markevery=sell_i, markerfacecolor='red', markeredgecolor='red')
    plt.show()

    print("buy:  {}\nhold: {}\nsell: {}".format(len(buy), len(hold), len(sell)))

    ans = input("do you want to save this? y/n")

    if ans.lower() != 'y':
        return

    random.shuffle(buy)
    random.shuffle(hold)
    random.shuffle(sell)

    min_len = min(len(hold), len(sell), len(buy))

    buy  = buy[:min_len]
    hold = hold[:min_len]
    sell = sell[:min_len]

    script_dir = os.path.dirname(__file__)
    rel_path = 'datasets/{}/{}'.format(pair.lower(), interval.lower())
    abs_backups_path = os.path.join(script_dir, rel_path)

    buy_path = os.path.join(abs_backups_path, 'buy')
    hold_path = os.path.join(abs_backups_path, 'hold')
    sell_path = os.path.join(abs_backups_path, 'sell')

    save_to_dir(buy, buy_path)
    save_to_dir(hold, hold_path)
    save_to_dir(sell, sell_path)

def load_dataset(data_paths, test_ratio=0.35):

    if type(data_paths) is not list:
        raise ValueError("data_paths must be a list")

    buy  = []
    hold = []
    sell = []

    # collecting data from files into lists
    for path in data_paths:

        buy_path  = os.path.join(path, 'buy')
        hold_path = os.path.join(path, 'hold')
        sell_path = os.path.join(path, 'sell')

        for file in os.listdir(buy_path):
            mat = np.load(os.path.join(buy_path, file))
            buy.append(mat)

        for file in os.listdir(hold_path):
            mat = np.load(os.path.join(hold_path, file))
            hold.append(mat)

        for file in os.listdir(sell_path):
            mat = np.load(os.path.join(sell_path, file))
            sell.append(mat)

    random.shuffle(buy)
    random.shuffle(hold)
    random.shuffle(sell)

    print(np.array(buy).shape)

    # arranging dataset
    X_train, y_train, X_test, y_test = [], [], [], []

    train_size = int((1 - test_ratio) * len(buy))

    X_train += buy[:train_size]
    X_train += hold[:train_size]
    X_train += sell[:train_size]

    y_train += train_size * [1]
    y_train += train_size * [0]
    y_train += train_size * [-1]

    assert (len(X_train) == 3 * train_size)
    assert (len(y_train) == 3 * train_size)

    # seed = 1024
    random.Random(1024).shuffle(X_train)
    random.Random(1024).shuffle(y_train)


    test_size = int(len(buy) - train_size)

    X_test += buy[:test_size]
    X_test += hold[:test_size]
    X_test += sell[:test_size]

    y_test += test_size * [1]
    y_test += test_size * [0]
    y_test += test_size * [-1]

    assert (len(X_test) == 3 * test_size)
    assert (len(y_test) == 3 * test_size)

    # seed = 1024
    random.Random(1024).shuffle(X_test)
    random.Random(1024).shuffle(y_test)

    return np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test)
