from numpy.random import uniform
from time import sleep
import ccxt
import time
import random
import numpy as np
from settings import *
import asyncio

'''
Order Call will return this

{
    'id':                '12345-67890:09876/54321', // string
    'datetime':          '2017-08-17 12:42:48.000', // ISO8601 datetime of 'timestamp' with milliseconds
    'timestamp':          1502962946216, // order placing/opening Unix timestamp in milliseconds
    'lastTradeTimestamp': 1502962956216, // Unix timestamp of the most recent trade on this order
    'status':     'open',         // 'open', 'closed', 'canceled'
    'symbol':     'ETH/BTC',      // symbol
    'type':       'limit',        // 'market', 'limit'
    'side':       'buy',          // 'buy', 'sell'
    'price':       0.06917684,    // float price in quote currency
    'amount':      1.5,           // ordered amount of base currency
    'filled':      1.1,           // filled amount of base currency
    'remaining':   0.4,           // remaining amount to fill
    'cost':        0.076094524,   // 'filled' * 'price' (filling price used where available)
    'trades':    [ ... ],         // a list of order trades/executions
    'fee': {                      // fee info, if available
        'currency': 'BTC',        // which currency the fee is (usually quote)
        'cost': 0.0009,           // the fee amount in that currency
        'rate': 0.002,            // the fee rate (if available)
    },
    'info': { ... },              // the original unparsed order structure as is
}
'''

binance_class = getattr(ccxt, 'binance')
binance = binance_class({
    'apiKey': environ.get('BINANCE_API_KEY'),
    'secret': environ.get('BINANCE_API_SECRET'),
    'timeout': 3000,
    'enableRateLimit': True,
    'adjustForTimeDifference': True
})

class Position:

    def __init__(self, pair, params):
        self.pair = pair
        self.symbol = binance_coins[self.pair]

        params['symbol'] = self.symbol

        if not ('limit' in params and
                'stop loss' in params and
                'take profit' in params and
                'test' in params and
                'date due' in params and
                'type' in params and
                'secure' in params and
                'amount' in params):

            raise KeyError

        params['type'] = params['type'].lower()

        if params['type'] not in position_instructions:
            raise ValueError('this order type is not supported')

        if params['take profit'] < 0 or params['stop loss'] < 0 or params['limit'] < 0:
            raise ValueError('take profit and stop loss have to be >=0')

        if type(params['secure']) is not bool or type(params['test']) is not bool:
            raise ValueError('secure and test must be bool type')

        if not (type(params['amount']) in [int, float] and
                type(params['limit']) in [int, float] and
                type(params['take profit']) in [int, float] and
                type(params['stop loss']) in [int, float]):

            raise ValueError('all prices have to be int or float')

        self.take_profit_price = params['take profit']
        self.stop_loss_price = params['stop loss']
        self.need_secure = params['secure']
        self.test = params['test']

        self.params = params.copy()
        self.is_secure = False

        self.id = None
        self.pos_amount = 0

        # TODO - change later
        self.risk_factor = uniform(0, 100)
        self.status = EMPTY

        self._orders = {'open': {},
                        'take profit': {},
                        'stop loss': {},
                        'close': {}}

    def update(self):

        if MODE == TEST:
            if self.status == WAIT_OPEN and np.random.randint(0, 100) % 10 == 0:
                self.pos_amount = self._orders['open']['amount']
                self.status = OPEN

            if self.status == OPEN and self.need_secure and not self.is_secure:
                self.secure()



            # TODO - make a part to simulate hitting stop_loss of take_profit
            return 0

        if self.status == CANCELED:
            return 0

        if self.status == CLOSED:
            return 0

        # checking for hit on stop-loss or take-profit
        if self.status == OPEN:

            take_profit_fill = 0
            stop_loss_fill = 0

            try:
                self._orders['open'] = binance.fetch_order(id=self._orders['open']['id'], symbol=self.symbol)
                self.pos_amount = self._orders['open']['fill']

                if self.need_secure:
                    self._take_profit_order = binance.fetch_order(id=self._take_profit_order['id'], symbol=self.symbol)
                    self._stop_loss_order = binance.fetch_order(id=self._stop_loss_order['id'], symbol=self.symbol)

                    take_profit_fill = self._take_profit_order['fill']
                    stop_loss_fill = self._stop_loss_order['fill']

            except Exception as e:
                print(e)
                return -1

            # TODO - there's a bug here. i need to prevent the position from closing
            #  while there might be open_order that's still being filled
            # checking if closed the amount that opened
            if take_profit_fill + stop_loss_fill == self.pos_amount:
                # TODO - change None to something else
                self._orders['close'] = None
                self.expose()
                self.status = CLOSED

            return 0

        if self.status == WAIT_OPEN:
            try:
                open_order = binance.fetch_order(id=self._orders['open']['id'], symbol=self.symbol)

                if open_order['fill'] > 0:
                    self.status = OPEN
                    self.pos_amount = open_order['fill']

                    if self.need_secure:
                        self.secure(take_profit=self.params['take profit'], stop_loss=self.params['stop loss'])

                elif open_order['status'] == 'canceled':
                    self.status = CANCELED

                elif open_order['status'] == 'open' and open_order['fill'] == 0:
                    self.status = WAIT_OPEN

                self._orders['open'] = open_order.copy()
                return 0

            except Exception as e:
                print(e)
                return -1

        return 0

    def open(self):

        if self.status != EMPTY or self._orders['open'] != {}:
            raise Exception('You are trying to open an open position')

        if MODE == TEST:
            open_order = self.test_order(params=self.params)
            self.id = open_order['id']
            self.status = WAIT_OPEN

            if self.params['type'] == 'market':
                open_order['status'] = 'closed'
                self.status = OPEN

            self._orders['open'] = open_order.copy()
            self.update()
            return 0

        try:
            self._orders['open'] = binance.create_order(symbol=self.symbol,
                                                        type=self.params['type'],
                                                        side=self.params['side'],
                                                        amount=self.params['amount'],
                                                        price=self.params['limit'],
                                                        params=self.params)
            self.id = self._orders['open']['id']

        except ccxt.RequestTimeout:
            # TODO - need last updated consider transferring to bot
            orders = binance.fetch_orders
            open_orders = []
            closed_orders = []
        except ccxt.InsufficientFunds:
            # TODO
            pass
        except Exception as e:
            print(e)
            return -1

        self.status = WAIT_OPEN

        # TODO - risk factor

        self.update()
        return 0

    def cancel(self):
        pass

    def close(self, close_price=None, **kwargs):
        pass

    def secure(self, take_profit=None, stop_loss=None):
        if self.is_secure:
            self._expose()

        self.need_secure = True

        if take_profit is not None and stop_loss is not None:
            self.set_exit_points(take_profit=take_profit, stop_loss=stop_loss)

    def _expose(self):

        """
        calling to this method will not change the need_secure attr, because we call it for the sake of exposing the position
        it's not a user made decision
        :return: 0 on success -1 on failure
        """

        if not self.is_secure:
            self.is_secure = False
            return 0


        if MODE == TEST:
            self._take_profit_order = None
            self._stop_loss_order = None
            self.is_secure = False
            return 0

        take_profit_order = self._orders['take profit']
        stop_loss_order = self._orders['stop loss']

        take_profit_canceled = False
        stop_loss_canceled = False

        try:
            if take_profit_order['status'] == 'open':
                binance.cancel_order(id=take_profit_order['id'], symbol=self.symbol)
                take_profit_canceled = True
        except Exception as e:
            print("Error while trying to cancel the takeprofit order")
            print(e)

        try:
            if stop_loss_order['status'] == 'open':
                binance.cancel_order(id=stop_loss_order['id'], symbol=self.symbol)
                stop_loss_canceled = True
        except Exception as e:
            print("Error while trying to cancel the stoploss order")
            print(e)

        # both canceled
        if take_profit_canceled and stop_loss_canceled:
            self.is_secure = False
            self._orders['take profit'] = {}
            self._orders['stop loss'] = {}
            return 0

        # exactly one order was not canceled
        if not take_profit_canceled or not stop_loss_canceled:
            self.is_secure = False

            if take_profit_canceled:
                self._orders['take profit'] = {}
            elif stop_loss_canceled:
                self._orders['stop loss'] = {}

            return -1

        # both were not canceled
        if not take_profit_canceled and not stop_loss_canceled:
            self.is_secure = True
            return -1

        # shouldn't get here
        return -1

    def expose(self):

        """
        called only by user, thus when called the need_secure flag is off
        :return:
        """

        self.need_secure = False
        return self._expose()

    def get_profit_percent(self, current_price=None):
        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit in percentages
        """

        pass

    def get_profit(self, current_price=None):
        pass

    def get_fee(self, price=None):

        assert len(self._orders['open']) > 0

        open_fee = self._orders['open']['fee']['cost']
        close_fee = 0

        if self.status == CLOSED:
            close_fee = self._orders['close']['fee']['cost']
        elif price is not None:
            close_fee = TAKER_FEE * price * self._orders['open']['amount']

        else:
            raise Exception("something went wrong with calculating fee")

        return close_fee + open_fee

    @staticmethod
    def test_order(params):

        fake_order = {'status': 'open',
                      'symbol': params['symbol'],
                      'type': params['type'],
                      'side': params['side'],
                      'limit': params['limit'],
                      'amount': params['amount'],
                      'filled': 0,
                      'remaining': params['amount'],
                      'cost': params['amount'] * params['limit'],
                      'id': random.randint(1000000, 9999999),
                      'fee': {'cost': params['amount'] * params['limit'] * TAKER_FEE}}

        return fake_order

    def get_orders_id_list(self):

        orders_ids = []

        if self._orders['open']:
            orders_ids.append(self._orders['open']['id'])

        if self._orders['close']:
            orders_ids.append(self._orders['close']['id'])

        if self.is_secure:
            assert self._take_profit_order and self._stop_loss_order

            orders_ids.append(self._take_profit_order['id'])
            orders_ids.append(self._stop_loss_order['id'])

        return orders_ids

    def set_exit_points(self, take_profit, stop_loss):
        pass

    def __getitem__(self, order):

        if order not in self._orders:
            return self._orders.copy()

        return self._orders[order]

class Long(Position):

    def __init__(self, pair, params):

        Position.__init__(self, pair=pair, params=params)

        # Long unique requirement
        if not params['stop loss'] <= params['limit'] <= params['take profit']:
            raise ValueError

    def open(self):
        self.params['side'] = 'buy'
        return super().open()

    def close(self, **kwargs):

        """
        when invoked the method will market sell the position regardless of market sate - should use only in emergencies
        :param close_price: for testing only
        :return:
        """

        self.update()

        close_price = kwargs.get('limit', None)

        # closing wait_open will invoke canceling
        if self.status == WAIT_OPEN:
            if self.cancel() != 0:
                return -1
            return 0

        if self._orders['open'] == {} or self.status != OPEN:
            return -1

        if MODE == TEST:
            if type(close_price) not in [int, float] or close_price < 0:
                raise ValueError('in testing you have to specify a valid closing price')
            
            close_params = {'amount': self._orders['open']['amount'],
                            'type': 'market',
                            'side': 'sell', 
                            'symbol': self.symbol,
                            'limit': close_price}

            self._orders['close'] = super().test_order(params=close_params).copy()
            if self._expose() == 0:
                self.status = CLOSED
                return 0
            return -1

        self._orders['close'] = binance.create_market_sell_order(symbol=self.symbol, amount=self._orders['open']['amount'])
        self.status = WAIT_CLOSE

        time.sleep(0.5)

        # update order
        self._orders['close'] = binance.fetch_order(id=self._orders['close']['id'], symbol=self.symbol)

        if self._orders['close']['status'] == 'open':
            self.status = WAIT_CLOSE

        if self._orders['close']['status'] == 'canceled':
            assert self._take_profit_order is None and self._stop_loss_order is None
            self.status = CANCELED

        if self._orders['close']['status'] == 'close':
            if self._expose() == 0:
                self.status = CLOSED
            else:
                self.status = ERROR

        return 0

    def secure(self, take_profit=None, stop_loss=None):

        def protect_test(position, t_amount, t_take_profit, t_stop_loss):
            position._orders['take profit'] = super().test_order(params={'symbol': self.symbol,
                                                                         'type': 'limit',
                                                                         'side': 'sell',
                                                                         'limit': t_take_profit,
                                                                         'amount': t_amount})

            position._orders['stop loss'] = super().test_order(params={'symbol': self.symbol,
                                                                       'type': 'limit',
                                                                       'side': 'sell',
                                                                       'limit': t_stop_loss,
                                                                       'amount': t_amount})

        if take_profit is None or stop_loss is None:
            take_profit = self.params['take profit']
            stop_loss = self.params['stop loss']

        if self._orders['open'] == {} or self.status != OPEN:
            return -1

        if not stop_loss <= self._orders['open']['limit'] <= take_profit:
            return -1

        if take_profit <= 0 or stop_loss <= 0:
            return -1

        super().secure(take_profit=take_profit, stop_loss=stop_loss)

        if MODE == TEST:
            protect_test(position=self, t_amount=self.pos_amount, t_take_profit=take_profit, t_stop_loss=stop_loss)
            self._orders['open']['status'] = 'closed'
            self.is_secure = True
            return 0

        # TODO - make special handling for binance errors like NoFunds etc

        take_profit_order_created = False
        stop_loss_order_created = False

        try:
            self._orders['stop loss'] = binance.create_order(symbol=self.symbol,
                                                             type='limit',
                                                             side='sell',
                                                             amount=self.pos_amount,
                                                             price=stop_loss,
                                                             params=self.params)
            stop_loss_order_created = True
        except Exception as e:
            print("Error with placing stop_loss limit")
            print(e)


        try:
            self._orders['take profit'] = binance.create_order(symbol=self.symbol,
                                                               type='limit',
                                                               side='sell',
                                                               amount=self.pos_amount,
                                                               price=take_profit,
                                                               params=self.params)
            take_profit_order_created = True
        except Exception as e:
            print("Error with placing take_profit limit")
            print(e)


        if not take_profit_order_created or not stop_loss_order_created:
            self.is_secure = False
            return -1

        self.is_secure = True
        return 0

    def cancel(self):

        """
        no closing_order can be cancel due to the fact that close is only for market which is always satisfied
        :return: 0 on success -1 on failure
        """

        self.update()

        if self.status != WAIT_OPEN:
            return -1

        if MODE == TEST:

            if self.status == WAIT_OPEN and self._orders['open'] != {}:
                if self._expose() != 0:
                    self.status = OPEN
                    return -1

                self.status = CANCELED
                return 0

            return -1

        # TODO - improve it so if a part of the order was filled we could still cancel
        if self.status != WAIT_OPEN or self._orders['open']['fill'] != 0:
            return -1

        try:
            if self._expose() != 0:
                self.status = OPEN
                return -1

            binance.cancel_order(id=self._orders['open']['id'], symbol=self.symbol)
            self.status = CANCELED

        except Exception as e:
            print("Error while trying to cancel the opening order")
            print(e)
            return -1

        return 0

    # TODO - fees
    def get_profit(self, current_price=None):

        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit
        """

        if (self.status == OPEN or self.status == WAIT_OPEN) and (MODE == TEST and current_price is None):
            raise ValueError("you have to specify a price")

        if type(current_price) not in [int, float] or current_price < 0:
            raise ValueError("price has to be non-negative int or float")

        if self.status is not CLOSED:
            # if the order is not closed a price should be supplied
            assert current_price is not None

            open_cost = self._orders['open']['cost']
            return current_price - open_cost - self.get_fee(price=current_price)

        open_cost = self._orders['open']['cost']
        closing_profit = self._orders['close']['cost']

        return closing_profit - open_cost - self.get_fee(price=current_price)

    # TODO - fees
    def get_profit_percent(self, current_price=None):
        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit in percentages
        """

        if (self.status == OPEN or self.status == WAIT_OPEN) and (MODE == TEST and current_price is None):
            raise ValueError("you have to specify a price")

        if type(current_price) not in [int, float] or current_price < 0:
            raise ValueError("price has to be non-negative int or float")

        return 100 * (self.get_profit(current_price=current_price) / self._orders['open']['cost'])

    def set_exit_points(self, take_profit, stop_loss):

        if take_profit < 0 or stop_loss < 0:
            return -1

        if not stop_loss < self.params['limit'] < take_profit:
            return -1

        if self._expose() != 0:
            return -1

        self.params['take profit'] = take_profit
        self.params['stop loss'] = stop_loss

        self.take_profit_price = take_profit
        self.stop_loss_price = stop_loss

        return 0


# TODO - Short fees
class Short(Position):
    def __init__(self, pair):
        Position.__init__(self, pair=pair)

    def open_market(self, amount, take_profit, stop_loss, secure=True, date_due=None, params={}):

        if amount <= 0 or take_profit <= 0 or stop_loss <= 0:
            return -1

        if stop_loss < take_profit:
            return -1

        if self.status != EMPTY or self._orders['open'] is not None:
            return -1

        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secure

        """
        TEST
        """

        if MODE == TEST:
            # for testing price has to be set
            assert params['limit']
            assert params['test']

            params['amount'] = amount
            params['type'] = 'market'
            params['side'] = 'sell'
            params['symbol'] = self.symbol

            self._orders['open'] = super().test_order(params=params)
            self.id = self._orders['open']['id']
            self.status = OPEN
            self._orders['open']['status'] = 'closed'
            return 0

        """
        END TEST
        """

        try:
            self._orders['open'] = binance.create_market_sell_order(symbol=self.symbol, amount=amount, params=params)
            self.id = self._orders['open']['id']

        except ccxt.RequestTimeout:
            # TODO - need last updated consider transferring to bot
            orders = binance.fetch_orders
            open_orders = []
            closed_orders = []
        except ccxt.InsufficientFunds:
            # TODO
            pass
        except Exception as e:
            print(e)
            return -1

        self.status = WAIT_OPEN

        # TODO - risk factor

        self.update()

        return 0

    def open_limit(self, amount, limit, take_profit, stop_loss, secure=True, date_due=None, params={}):

        if amount <= 0 or limit <= 0 or take_profit <= 0 or stop_loss <= 0:
            return -1

        if not take_profit <= limit <= stop_loss:
            return -1

        if self.status != EMPTY or self._orders['open'] is not None:
            return -1

        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secure

        """
        TEST
        """

        if MODE == TEST:
            assert params['test']

            params['amount'] = amount
            params['limit'] = limit
            params['type'] = 'limit'
            params['side'] = 'sell'
            params['symbol'] = self.symbol

            self._orders['open'] = super().test_order(params=params)
            self.id = self._orders['open']['id']
            self.status = WAIT_OPEN
            return 0

        """
        END TEST
        """

        try:
            self._orders['open'] = binance.create_limit_sell_order(self.symbol, amount, limit, secure, params)
            self.id = self._orders['open']['id']

        except ccxt.RequestTimeout:
            # TODO - need last updated consider transferring to bot
            orders = binance.fetch_orders
            open_orders = []
            closed_orders = []

        except ccxt.InsufficientFunds:
            # TODO
            pass

        except Exception as e:
            print(e)
            return -1

        self.status = WAIT_OPEN

        # TODO - risk factor

        self.update()

        return 0

    def close(self, params={}):

        """
        when invoked the method will market sell the position regardless of market sate - should use only in emergencies
        :param price: for testing only
        :return:
        """

        self.update()

        # closing wait_open will invoke canceling
        if self.status == WAIT_OPEN:
            if self.cancel() != 0:
                return -1
            return 0

        if self._orders['open'] is None or self.status != OPEN:
            return -1

        if MODE == TEST:
            assert params['test']
            assert params['limit']

            params['amount'] = self._orders['open']['amount'] * (self._orders['open']['limit'] / limit)
            params['type'] = 'market'
            params['side'] = 'buy'
            params['symbol'] = self.symbol

            self._orders['close'] = super().test_order(params=params)
            if self._expose() == 0:
                self.status = CLOSED
                return 0
            return -1

        self._orders['close'] = binance.create_market_buy_order(symbol=self.symbol, amount=self._orders['open']['amount'])
        self.status = WAIT_CLOSE

        time.sleep(0.5)

        # update order
        self._orders['close'] = binance.fetch_order(id=self._orders['close']['id'], symbol=self.symbol)

        if self._orders['close']['status'] == 'open':
            self.status = WAIT_CLOSE

        if self._orders['close']['status'] == 'canceled':
            assert self._take_profit_order is None and self._stop_loss_order is None
            self.status = CANCELED

        if self._orders['close']['status'] == 'close':
            if self._expose() == 0:
                self.status = CLOSED
            else:
                self.status = ERROR

        return 0

    def secure(self, take_profit, stop_loss, params):

        def protect_test(position, t_amount, t_take_profit, t_stop_loss):
            position._take_profit_order = super().test_order(params={'symbol': self.symbol,
                                                                     'type': 'limit',
                                                                     'side': 'buy',
                                                                     'price': t_take_profit,
                                                                     'amount': t_amount})

            position._stop_loss_order = super().test_order(params={'symbol': self.symbol,
                                                                   'type': 'limit',
                                                                   'side': 'buy',
                                                                   'price': t_stop_loss,
                                                                   'amount': t_amount})

        if not take_profit <= self._orders['open']['limit'] <= stop_loss:
            return -1

        if self._orders['open'] is None or (self.status != WAIT_OPEN and self.status != OPEN):
            return -1

        super().secure(take_profit=take_profit, stop_loss=stop_loss, params=params)

        if MODE == TEST:
            protect_test(position=self, t_amount=self.pos_amount, t_take_profit=take_profit, t_stop_loss=stop_loss)
            self._orders['open']['status'] = 'closed'
            self.is_secure = True
            return 0

        # TODO - make special handling for binance errors like NoFunds etc

        take_profit_order_created = False
        stop_loss_order_created = False

        try:
            self._take_profit_order = binance.create_limit_buy_order(symbol=self.symbol, amount=self.pos_amount,
                                                                     price=take_profit, params=params)
            take_profit_order_created = True
        except Exception as e:
            print("Error with placing take_profit limit")
            print(e)

        try:
            self._stop_loss_order = binance.create_limit_buy_order(symbol=self.symbol, amount=self.pos_amount,
                                                                   price=stop_loss, params=params)
            stop_loss_order_created = True
        except Exception as e:
            print("Error with placing stop_loss limit")
            print(e)

        if not take_profit_order_created or not stop_loss_order_created:
            self.is_secure = False
            return -1

        self.is_secure = True
        return 0

    def cancel(self):

        """
        no closing_order can be cancel due to the fact that close is only for market which is always satisfied
        :return: 0 on success -1 on failure
        """

        self.update()

        if self.status != WAIT_OPEN:
            return -1

        if MODE == TEST:

            if self.status == WAIT_OPEN and self._orders['open'] and self._orders['close'] is None:
                self._expose()
                self.status = CANCELED
                return 0

            return -1

        if self.status == WAIT_OPEN and self._orders['open'] and self._orders['close'] is None:

            try:
                if self._expose() != 0:
                    self.status = ERROR
                    return -1

                binance.cancel_order(id=self._orders['open']['id'], symbol=self.symbol)
                self.status = CANCELED

            except Exception as e:
                print("Error while trying to cancel the opening order")
                print(e)
                return -1

        return 0

    # TODO - fees
    def get_profit(self, current_price=None):

        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit
        """

        if self.status is not CLOSED:
            # if the order is not closed a price should be supplied
            assert current_price is not None

            open_cost = self._orders['open']['cost']
            return current_price - open_cost

        assert self._orders['close'] is not None

        open_amount = self._orders['open']['amount']
        closing_amount = self._orders['close']['amount']

        return closing_amount - open_amount

    # TODO - fees
    def get_profit_percent(self, current_price=None):
        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit in percentages
        """

        if self.status is not CLOSED:
            # if the order is not closed a price should be supplied
            assert current_price is not None

            open_cost = self._orders['open']['cost']
            return 100 * ((current_price - open_cost) / open_cost)

        assert self._orders['close'] is not None

        open_amount = self._orders['open']['amount']
        profit = self.get_profit(current_price=current_price)

        return 100 * (profit / open_amount)


class Scalp(Position):

    def __init__(self, pair):
        Position.__init__(self, pair=pair)
        self.long = Long(pair=pair)
        self.short = Short(pair=pair)

    def open(self, amount, upper_bound, lower_bound, date_due=None, params={}):
        pass
