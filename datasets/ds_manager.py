
from config import *
import os
import shutil
import numpy as np
import random
import matplotlib.pyplot as plt

"""
Dataset Structure is:

datasets

    my_ds

        meta.txt (contains the parameters used for the dataset)
        
        train
            buy
                * npy matrices
            
            hold
                * npy matrices
                
            sell
                * npy matrices

        validation
            buy
                * npy matrices
                
            hold
                * npy matrices
            
            sell
                * npy matrices
"""

def save_ds(ds_path, buy, hold, sell):

    for i in range(len(buy)):
        path = os.path.join(os.path.join(ds_path, 'buy'), "{}".format(i + 1))
        np.save(path, buy[i])

    for i in range(len(buy)):
        path = os.path.join(os.path.join(ds_path, 'hold'), "{}".format(i + 1))
        np.save(path, hold[i])

    for i in range(len(buy)):
        path = os.path.join(os.path.join(ds_path, 'sell'), "{}".format(i + 1))
        np.save(path, sell[i])

def create_dir(ds_name):

    ds_path = os.path.join(DS_DIR, ds_name)

    train_path = os.path.join(ds_path, 'train')
    val_path   = os.path.join(ds_path, 'validation')

    if os.path.exists(ds_path):
        ans = input("dataset already exists, do you want to rewrite? y/n")
        if ans.lower() != 'y':
            return -1

        shutil.rmtree(ds_path)

    os.makedirs(ds_path)

    os.makedirs(train_path)
    os.makedirs(os.path.join(train_path, 'buy'))
    os.makedirs(os.path.join(train_path, 'hold'))
    os.makedirs(os.path.join(train_path, 'sell'))

    os.makedirs(val_path)
    os.makedirs(os.path.join(val_path, 'buy'))
    os.makedirs(os.path.join(val_path, 'hold'))
    os.makedirs(os.path.join(val_path, 'sell'))

    return 0

def create_meta(ds_name, param_list, feature_size, train_data_list, val_data_list):

    param_len = len(param_list)

    ds_path   = os.path.join(DS_DIR, ds_name)
    meta_path = os.path.join(ds_path, 'meta.txt')

    f = open(meta_path, "w+")

    f.write("Num of parameters:  {}\n".format(param_len))
    f.write("Feature size:       {}\n".format(feature_size))

    f.write("\nParameters:\n")
    for param in param_list:
        f.write("\t{}\n".format(param))

    f.write("\nTrain Data:\n")
    for data in train_data_list:
        f.write("\t{:<10}{:>10}\n".format(data.pair, data.interval))

    f.write("\nValidation Data:\n")
    for data in val_data_list:
        f.write("\t{:<10}{:>10}\n".format(data.pair, data.interval))

    f.close()

def create_matrix(df, cols):

    mat = []

    for col in cols:
        arr = np.array(df[col].values)
        norm = np.linalg.norm(arr, axis=0, keepdims=True)
        if norm != 0:
            arr = arr / norm

        mat.append(arr)

    return np.array(mat).flatten()

def create_buy_hold_sell(data_list, params, det_y_true, past_size, future_size):

    ret_buy  = []
    ret_hold = []
    ret_sell = []

    for data in data_list:

        buy  = []
        hold = []
        sell = []

        buy_i  = []
        hold_i = []
        sell_i = []

        df       = data.df[:-VAL_SIZE]
        pair     = data.pair
        interval = data.interval

        iterations = 0 if df.shape[0] - past_size - future_size < 0 else df.shape[0] - past_size - future_size

        prices = np.array(df['close'].values)
        timestamps = np.array(df['close_timestamp'].values)

        # we skip 512 candles in the beginning to avoid NaN
        for i in range(512, iterations):

            past   = df.iloc[i:past_size + i]
            future = df.iloc[past_size + i:past_size + future_size + i]
            window = df.iloc[i:past_size + future_size + i]

            matrix = create_matrix(past, params)
            if np.any(np.isnan(matrix)):
                continue

            y_true = det_y_true(window, past_size)

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
            continue

        min_len = min(len(hold), len(sell), len(buy))

        random.shuffle(buy)
        random.shuffle(hold)
        random.shuffle(sell)

        ret_buy  += buy[:min_len]
        ret_hold += hold[:min_len]
        ret_sell += sell[:min_len]

    return ret_buy, ret_hold, ret_sell

def create_dataset(ds_name, params, train_list, val_list, det_y_true, past_size=128, future_size=32):

    """
    :param ds_name: a string - a folder with this name will be opened
    :param params: list of parameters from csv files to put in the matrix
    :param train_list: list of datas
    :param val_list: list of datas
    :param det_y_true: a function that gets (window, current_index) window is df and current index says where we are in the window
    :param past_size: how much back we look
    :param future_size: how much forward we look
    :return: ds_path
    """

    # past is the data we are exporting because we want to train the bot to infer future from past data
    if create_dir(ds_name) == -1:
        return os.path.join(DS_DIR, ds_name)

    create_meta(ds_name, params, past_size, train_list, val_list)

    train_buy, train_hold, train_sell = create_buy_hold_sell(train_list, params, det_y_true, past_size, future_size)
    train_path = os.path.join(os.path.join(DS_DIR, ds_name), 'train')
    save_ds(train_path, train_buy, train_hold, train_sell)

    val_buy, val_hold, val_sell = create_buy_hold_sell(val_list, params, det_y_true, past_size, future_size)
    val_path = os.path.join(os.path.join(DS_DIR, ds_name), 'validation')
    save_ds(val_path, val_buy, val_hold, val_sell)

    return os.path.join(DS_DIR, ds_name)

def load_dataset(ds_path, test_ratio=0.35):

    buy_ans  = [[1, 0, 0]]
    hold_ans = [[0, 1, 0]]
    sell_ans = [[0, 0, 1]]

    buy, hold, sell = [], [], []

    train_path = os.path.join(ds_path, 'train')

    buy_path  = os.path.join(train_path, 'buy')
    hold_path = os.path.join(train_path, 'hold')
    sell_path = os.path.join(train_path, 'sell')

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

    # arranging dataset
    X_train, y_train, X_test, y_test = [], [], [], []

    train_size = int((1 - test_ratio) * len(buy))

    X_train += buy[:train_size]
    X_train += hold[:train_size]
    X_train += sell[:train_size]

    y_train += train_size * buy_ans
    y_train += train_size * hold_ans
    y_train += train_size * sell_ans

    # seed = 1024
    random.Random(1024).shuffle(X_train)
    random.Random(1024).shuffle(y_train)

    test_size = int(len(buy) - train_size)

    X_test += buy[:test_size]
    X_test += hold[:test_size]
    X_test += sell[:test_size]

    y_test += test_size * buy_ans
    y_test += test_size * hold_ans
    y_test += test_size * sell_ans

    # seed = 1024
    random.Random(1024).shuffle(X_test)
    random.Random(1024).shuffle(y_test)

    return np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test)




