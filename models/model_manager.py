
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from config import *
import numpy as np
import h5py
from tensorflow.keras import backend, models
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import concatenate, Dense, Input, Dropout, Activation
from keras.utils import to_categorical
import os
import dataset
from data import Data
import sys

sys.path.append(DS_DIR)
import ds_manager

class PredModel:

    @staticmethod
    def create_model(input_shape):

        a = Input(shape=(input_shape,))
        b = Dense(2048, activation='relu')(a)
        b = Dropout(0.25)(b)
        b = Dense(1024, activation='relu')(b)
        b = Dropout(0.25)(b)
        b = Dense(128, activation='relu')(b)
        b = Dropout(0.25)(b)
        b = Dense(512, activation='relu')(b)
        b = Dense(3, activation='softmax')(b)
        m = Model(inputs=a, outputs=b)
        m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        # print(m.summary())

        return m

    def __init__(self, name, ds_path, input_shape):

        self.name    = name
        self.ds_path = ds_path

        self.model_path = os.path.join(os.path.join(MODEL_DIR, self.name), '{}.h5'.format(self.name))
        self.hist_path  = os.path.join(os.path.join(MODEL_DIR, self.name), '{}_hist.txt'.format(self.name))
        self.meta_path  = os.path.join(os.path.join(MODEL_DIR, self.name), '{}_meta.txt'.format(self.name))

        # if first time
        if not os.path.exists(self.model_path):
            self.model = self.create_model(input_shape)
            self._save()

        # for loading if it exists
        else:
            self.model = models.load_model(self.model_path)

    def _save(self, create_meta=True, create_hist=True):

        model_path = os.path.join(MODEL_DIR, self.name)

        if not os.path.exists(model_path):
            os.makedirs(model_path)

        self.model.save(self.model_path)

        if create_meta:
            f = open(self.meta_path, "w+")
            f.write("--------------------- Trained on ---------------------\n")
            f.write("{}\n".format(self.ds_path.split('\\')[-1]))
            f.write("------------------------------------------------------\n\n")
            self.model.summary(print_fn=lambda x: f.write(x + '\n'))
            f.close()

        if create_hist:
            f = open(self.hist_path, "w+")
            f.close()

    def fit(self, test_ratio=0.35, epochs=5, verbose=2):

        X_train, y_train, X_test, y_test = ds_manager.load_dataset(self.ds_path, test_ratio=test_ratio)

        f = open(self.hist_path, "a")
        f.write("\ntrained {:>4} epochs\n".format(epochs))

        history = self.model.fit(X_train, y_train, epochs=epochs, validation_data=(X_test, y_test), verbose=verbose)
        f.write("loss:      {}\ntrain_acc: {}\nval_acc:   {}\n".format(history.history['loss'][-1],
                                                                       history.history['accuracy'][-1],
                                                                       history.history['val_accuracy'][-1]))
        f.close()

        self._save(create_meta=False, create_hist=False)


    def evaluate(self, X, y_true, rule):

        y_pred = self.model.predict(X)

        assert (type(y_pred) == np.ndarray)
        assert (type(y_true) == np.ndarray)

        assert (y_pred.shape == y_true.shape)

        y_pred_list = list(y_pred)
        y_true_list = list(y_true)

        right_answers = 0
        for i in range(len(y_pred_list)):
            ans = rule(y_pred_list[i])
            if np.all(ans == y_true_list[i]):
                right_answers += 1

        return float(right_answers / y_true.shape[0])
