

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import numpy as np
from tensorflow.keras import backend
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import concatenate, Dense, Input, Dropout, Activation
from keras.utils import to_categorical

import dataset
from data import Data



def create(input_shape):
    # m = Sequential()
    # m.add(Dense(32, input_shape=(input_shape, )))
    # m.add(Activation('relu'))
    # m.add(Dense(3))
    # # model.add(Activation('softmax'))
    a = Input(shape=(input_shape, ))
    b = Dense(512, activation='relu')(a)
    b = Dense(128, activation='relu')(b)
    b = Dense(16, activation='relu')(b)
    b = Dense(3, activation='softmax')(b)
    m = Model(inputs=a, outputs=b)
    m.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(m.summary())
    return m


if __name__ == '__main__':
    # params = ['bollinger_l_indicator',
    #           'bollinger_h_indicator',
    #           'rsi',
    #           'stochastic',
    #           'volume',
    #           'last_candle_change',
    #           'macd_signal',
    #           'num_of_trades']
    #
    # ds = Data("ETHUSDT", '1h')
    # dataset.create_new_dataset(ds, params)

    X_train, y_train, X_test, y_test = dataset.load_dataset(
        [r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\datasets\ethusdt\1h'])
    # assert not np.isnan(np.sum(X_train))
    # assert not np.isnan(np.sum(y_train))
    # assert not np.isnan(np.sum(y_test))
    # assert not np.isnan(np.sum(X_test))
    print("X_train.shape:     {}".format(X_train.shape))
    print("y_train.shape:     {}".format(y_train.shape))
    print("X_test.shape:      {}".format(X_test.shape))
    print("y_test.shape:      {}".format(y_test.shape))

    ones = np.ones(y_train.shape).astype('int')
    y_train = y_train.astype('int')
    y_train += ones

    ones = np.ones(y_test.shape).astype('int')
    y_test = y_test.astype('int')
    y_test  += ones

    model = create(X_train.shape[1])

    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

