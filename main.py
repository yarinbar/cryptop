
from config import *
import sys
import numpy as np

sys.path.append(DS_DIR)
sys.path.append(MODEL_DIR)

import ds_manager
from model_manager import PredModel
from data import Data



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


if __name__ == '__main__':

    params = ['bollinger_l_indicator',
              'bollinger_h_indicator',
              'rsi',
              'stochastic',
              'volume',
              'last_candle_change',
              'macd_signal',
              'num_of_trades']

    train_list = [Data('btcusdt', '1h'),
                  Data('ethbtc', '2h'),
                  Data('ltcusdt', '1h'),
                  Data('bnbusdt', '1h'),
                  Data('xrpusdt', '1h')]

    val_list   = [Data('ethusdt', '1h')]

    ds_path = ds_manager.create_dataset('8_params', params, train_list, val_list, determine_y_true)

    X_train, y_train, X_test, y_test = ds_manager.load_dataset(ds_path)

    my_model = PredModel('my_first', ds_path, 1024)

    my_model.fit()


