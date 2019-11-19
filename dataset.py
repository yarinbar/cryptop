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
import pickle
from random import uniform
import os
from pandas import Series
import pandas as pd
from strategy import Strategy
import random
import matplotlib.pyplot as plt

def determine_y_true(future):

    change = np.array(future['last_candle_change'].values)

    max_change = np.amax(change)
    min_change = np.amin(change)

    num_of_candles = change.shape[0]
    down = np.where(change < -1)[0].shape[0]
    up   = np.where(change > 1)[0].shape[0]

    if up / num_of_candles > 0.5 and max_change > 4:
        return 1

    if down / num_of_candles > 0.5 and min_change < -4:
        return -1

    return 0


def create_matrix(df, cols):

    mat = []

    for col in cols:
        mat.append(np.array(df[col].values))

    return np.array(mat)

def create_dir(pair):

    script_dir = os.path.dirname(__file__)
    rel_path = 'datasets/{}'.format(pair.lower())
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


def create_dataset(data, cols, past_size=128, future_size=16):

    df   = data.df
    pair = data.pair

    create_dir(pair)

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

        matrix = create_matrix(past, cols)
        y_true = determine_y_true(future)

        if y_true == 1:
            buy_i.append(i)
            buy.append(matrix)

        if y_true == 0:
            hold_i.append(i)
            hold.append(matrix)

        if y_true == -1:
            sell_i.append(i)
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

    random.shuffle(buy)
    random.shuffle(hold)
    random.shuffle(sell)

    print("buy:  {}\nhold: {}\nsell: {}".format(len(buy), len(hold), len(sell)))

    min_len = min(len(hold), len(sell), len(buy))

    buy  = buy[:min_len]
    hold = hold[:min_len]
    sell = sell[:min_len]

    script_dir = os.path.dirname(__file__)
    rel_path = 'datasets/{}'.format(pair.lower())
    abs_backups_path = os.path.join(script_dir, rel_path)

    buy_path = os.path.join(abs_backups_path, 'buy')
    hold_path = os.path.join(abs_backups_path, 'hold')
    sell_path = os.path.join(abs_backups_path, 'sell')

    save_to_dir(buy, buy_path)
    save_to_dir(hold, hold_path)
    save_to_dir(sell, sell_path)

