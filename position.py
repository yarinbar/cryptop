from numpy.random import uniform
from time import sleep
import ccxt
import time
import random
import numpy as np
from settings import *

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


class Position:

    def __init__(self, pair):
        self.pair = pair
        self.symbol = binance_coins[self.pair]
        self.id = None
        self.pos_amount = 0

        # TODO - change later
        self.risk_factor = uniform(0, 100)
        self.status = EMPTY

        self.target_price = None
        self.stop_loss = None
        self.date_due = None

        self._open_order = None
        self._close_order = None
        self._take_profit_order = None
        self._stop_loss_order = None

        self.need_secure = True
        self.is_secured = False

    def update(self):

        if MODE == TEST:
            if self.status == WAIT_OPEN and np.random.randint(0, 100) % 10 == 0:
                self.pos_amount = self._open_order['amount']

                if self.need_secure and not self.is_secured:

                    self.secure(target_price=self.target_price,
                                stop_loss=self.stop_loss,
                                params={'test': True})

                self.status = OPEN

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
                self._open_order = binance.fetch_order(id=self._open_order['id'], symbol=self.symbol)
                self.pos_amount = self._open_order['fill']

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
                self._close_order = None
                self.expose()
                self.status = CLOSED

            return 0

        if self.status == WAIT_OPEN:
            try:
                self._open_order = binance.fetch_order(id=self._open_order['id'], symbol=self.symbol)

                if self._open_order['fill'] > 0:
                    self.status = OPEN
                    self.pos_amount = self._open_order['fill']

                    if self.need_secure:
                        self.secure(target_price=self.target_price, stop_loss=self.stop_loss, params={})

                elif self._open_order['status'] == 'canceled':
                    self.status = CANCELED

                elif self._open_order['status'] == 'open' and self._open_order['fill'] == 0:
                    self.status = WAIT_OPEN

                return 0


            except Exception as e:
                print(e)
                return -1

        return 0

    def cancel(self):
        pass

    def close(self):
        pass

    def secure(self, target_price, stop_loss, params):
        if self.is_secured:
            self.expose()

        self.need_secure = True

    def expose(self):

        if not self.is_secured:
            self.need_secure = False
            self.is_secured = False
            return 0

        self.need_secure = False

        if MODE == TEST:
            self._take_profit_order = None
            self._stop_loss_order = None
            self.is_secured = False
            return 0

        take_profit_canceled = False
        stop_loss_canceled = False

        try:
            if self._take_profit_order['status'] == 'open':
                binance.cancel_order(id=self._take_profit_order['id'], symbol=self.symbol)
                take_profit_canceled = True
        except Exception as e:
            print("Error while trying to cancel the takeprofit order")
            print(e)

        try:
            if self._stop_loss_order['status'] == 'open':
                binance.cancel_order(id=self._stop_loss_order['id'], symbol=self.symbol)
                stop_loss_canceled = True
        except Exception as e:
            print("Error while trying to cancel the stoploss order")
            print(e)

        # both canceled
        if take_profit_canceled and stop_loss_canceled:
            self.is_secured = False
            self._take_profit_order = None
            self._stop_loss_order = None
            return 0

        # exactly one order was not canceled
        if not take_profit_canceled or not stop_loss_canceled:
            self.is_secured = False

            if take_profit_canceled:
                self._take_profit_order = None
            elif stop_loss_canceled:
                self._stop_loss_order = None

            return -1

        # both were not canceled
        if not take_profit_canceled and not stop_loss_canceled:
            self.is_secured = True
            return -1

        # shouldn't get here
        return -1

    def get_profit_percent(self, current_price=None):
        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit in percentages
        """

        pass

    def get_profit(self, current_price=None):
        pass

    def get_fee(self, price=None):

        assert self._open_order is not None

        open_fee = self._open_order['fee']['cost']
        close_fee = 0

        if price is not None:
            close_fee = TAKER_FEE * price * self._open_order['amount']
        elif self._close_order is not None:
            close_fee = self._close_order['fee']['cost']
        else:
            return -1

        return close_fee + open_fee

    @staticmethod
    def test_order(params):

        fake_order = {'status': 'open',
                      'symbol': params['symbol'],
                      'type': params['type'],
                      'side': params['side'],
                      'price': params['price'],
                      'amount': params['amount'],
                      'filled': 0,
                      'remaining': params['amount'],
                      'cost': params['amount'] * params['price'],
                      'id': random.randint(1000000, 9999999),
                      'fee': {'cost': params['amount'] * params['price'] * TAKER_FEE}}

        return fake_order

    def get_orders_id_list(self):

        orders_ids = []

        if self._open_order:
            orders_ids.append(self._open_order['id'])

        if self._close_order:
            orders_ids.append(self._close_order['id'])

        if self.is_secured:
            assert self._take_profit_order and self._stop_loss_order

            orders_ids.append(self._take_profit_order['id'])
            orders_ids.append(self._stop_loss_order['id'])

        return orders_ids

    def __getitem__(self, order):

        orders = {'open': self._open_order,
                  'close': self._close_order,
                  'take profit': self._take_profit_order,
                  'stop loss': self._stop_loss_order}

        if order == 'all':
            return orders

        return orders[order]


class Long(Position):

    def __init__(self, pair):
        Position.__init__(self, pair=pair)

    def open_market(self, amount, target_price, stop_loss, secured=True, date_due=None, params={}):

        if amount <= 0 or target_price <= 0 or stop_loss <= 0:
            return -1

        if not stop_loss <= target_price:
            return -1

        if self.status != EMPTY or self._open_order is not None:
            return -1

        self.target_price = target_price
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secured

        """
        TEST
        """

        if MODE == TEST:
            # for testing price has to be set
            assert params['price']
            assert params['test']

            params['amount'] = amount
            params['type'] = 'market'
            params['side'] = 'buy'
            params['symbol'] = self.symbol

            self._open_order = super().test_order(params=params)
            self.id = self._open_order['id']
            self.status = OPEN
            self._open_order['status'] = 'closed'
            return 0

        """
        END TEST
        """

        try:
            self._open_order = binance.create_market_buy_order(symbol=self.symbol, amount=amount, params=params)
            self.id = self._open_order['id']

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

    def open_limit(self, amount, limit, target_price, stop_loss, secured=True, date_due=None, params={}):

        if amount <= 0 or limit <= 0 or target_price <= 0 or stop_loss <= 0:
            return -1

        if not stop_loss <= limit <= target_price:
            return -1

        if self.status != EMPTY or self._open_order is not None:
            return -1

        self.target_price = target_price
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secured

        """
        TEST
        """

        if MODE == TEST:
            assert params['test']

            params['amount'] = amount
            params['price'] = limit
            params['type'] = 'limit'
            params['side'] = 'buy'
            params['symbol'] = self.symbol

            self._open_order = super().test_order(params=params)
            self.id = self._open_order['id']
            self.status = WAIT_OPEN
            return 0

        """
        END TEST
        """

        try:
            self._open_order = binance.create_limit_buy_order(self.symbol, amount, limit, secured, params)
            self.id = self._open_order['id']

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

        if self._open_order is None or self.status != OPEN:
            return -1

        if MODE == TEST:
            assert params['test']
            assert params['price']

            params['price'] = params['price']
            params['amount'] = self._open_order['amount']
            params['type'] = 'market'
            params['side'] = 'sell'
            params['symbol'] = self.symbol

            self._close_order = super().test_order(params=params)
            if self.expose() == 0:
                self.status = CLOSED
                return 0
            return -1

        self._close_order = binance.create_market_sell_order(symbol=self.symbol, amount=self._open_order['amount'])
        self.status = WAIT_CLOSE

        time.sleep(0.5)

        # update order
        self._close_order = binance.fetch_order(id=self._close_order['id'], symbol=self.symbol)

        if self._close_order['status'] == 'open':
            self.status = WAIT_CLOSE

        if self._close_order['status'] == 'canceled':
            assert self._take_profit_order is None and self._stop_loss_order is None
            self.status = CANCELED

        if self._close_order['status'] == 'close':
            if self.expose() == 0:
                self.status = CLOSED
            else:
                self.status = ERROR

        return 0

    def secure(self, target_price, stop_loss, params):

        def protect_test(position, t_amount, t_target_price, t_stop_loss):
            position._take_profit_order = super().test_order(params={'symbol': self.symbol,
                                                                     'type': 'limit',
                                                                     'side': 'sell',
                                                                     'price': t_target_price,
                                                                     'amount': t_amount})

            position._stop_loss_order = super().test_order(params={'symbol': self.symbol,
                                                                   'type': 'limit',
                                                                   'side': 'sell',
                                                                   'price': t_stop_loss,
                                                                   'amount': t_amount})

        if not stop_loss <= self._open_order['price'] <= target_price:
            return -1

        if self._open_order is None or (self.status != WAIT_OPEN and self.status != OPEN):
            return -1

        super().secure(target_price=target_price, stop_loss=stop_loss, params=params)

        if MODE == TEST:
            protect_test(position=self, t_amount=self.pos_amount, t_target_price=target_price, t_stop_loss=stop_loss)
            self._open_order['status'] = 'closed'
            self.is_secured = True
            return 0

        # TODO - make special handling for binance errors like NoFunds etc

        take_profit_order_created = False
        stop_loss_order_created = False

        try:
            self._take_profit_order = binance.create_limit_sell_order(symbol=self.symbol, amount=self.pos_amount,
                                                                      price=target_price, params=params)
            take_profit_order_created = True
        except Exception as e:
            print("Error with placing target_price limit")
            print(e)

        try:
            self._stop_loss_order = binance.create_limit_sell_order(symbol=self.symbol, amount=self.pos_amount,
                                                                    price=stop_loss, params=params)
            stop_loss_order_created = True
        except Exception as e:
            print("Error with placing stop_loss limit")
            print(e)

        if not take_profit_order_created or not stop_loss_order_created:
            self.is_secured = False
            return -1

        self.is_secured = True
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

            if self.status == WAIT_OPEN and self._open_order and self._close_order is None:
                self.expose()
                self.status = CANCELED
                return 0

            return -1

        if self.status == WAIT_OPEN and self._open_order and self._close_order is None:

            try:
                if self.expose() != 0:
                    self.status = ERROR
                    return -1

                binance.cancel_order(id=self._open_order['id'], symbol=self.symbol)
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

            open_cost = self._open_order['cost']
            return current_price - open_cost

        assert self._close_order is not None

        open_cost = self._open_order['cost']
        closing_profit = self._close_order['cost']

        return closing_profit - open_cost - self.get_fee()

    # TODO - fees
    def get_profit_percent(self, current_price=None):
        """
        :param current_price: (OPTIONAL) for seeing what the profit would have been now
        :return: profit in percentages
        """

        if self.status is not CLOSED:
            # if the order is not closed a price should be supplied
            assert current_price is not None

            open_cost = self._open_order['cost']
            return 100 * ((current_price - open_cost) / open_cost)

        assert self._close_order is not None

        open_cost = self._open_order['cost']
        close_price = self._close_order['cost']

        return 100 * ((close_price - open_cost - self.get_fee()) / open_cost)


# TODO - Short fees
class Short(Position):
    def __init__(self, pair):
        Position.__init__(self, pair=pair)

    def open_market(self, amount, target_price, stop_loss, secured=True, date_due=None, params={}):

        if amount <= 0 or target_price <= 0 or stop_loss <= 0:
            return -1

        if stop_loss < target_price:
            return -1

        if self.status != EMPTY or self._open_order is not None:
            return -1

        self.target_price = target_price
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secured

        """
        TEST
        """

        if MODE == TEST:
            # for testing price has to be set
            assert params['price']
            assert params['test']

            params['amount'] = amount
            params['type'] = 'market'
            params['side'] = 'sell'
            params['symbol'] = self.symbol

            self._open_order = super().test_order(params=params)
            self.id = self._open_order['id']
            self.status = OPEN
            self._open_order['status'] = 'closed'
            return 0

        """
        END TEST
        """

        try:
            self._open_order = binance.create_market_sell_order(symbol=self.symbol, amount=amount, params=params)
            self.id = self._open_order['id']

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

    def open_limit(self, amount, limit, target_price, stop_loss, secured=True, date_due=None, params={}):

        if amount <= 0 or limit <= 0 or target_price <= 0 or stop_loss <= 0:
            return -1

        if not target_price <= limit <= stop_loss:
            return -1

        if self.status != EMPTY or self._open_order is not None:
            return -1

        self.target_price = target_price
        self.stop_loss = stop_loss
        self.date_due = date_due

        self.need_secure = secured

        """
        TEST
        """

        if MODE == TEST:
            assert params['test']

            params['amount'] = amount
            params['price'] = limit
            params['type'] = 'limit'
            params['side'] = 'sell'
            params['symbol'] = self.symbol

            self._open_order = super().test_order(params=params)
            self.id = self._open_order['id']
            self.status = WAIT_OPEN
            return 0

        """
        END TEST
        """

        try:
            self._open_order = binance.create_limit_sell_order(self.symbol, amount, limit, secured, params)
            self.id = self._open_order['id']

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

        if self._open_order is None or self.status != OPEN:
            return -1

        if MODE == TEST:
            assert params['test']
            assert params['price']

            params['price'] = params['price']
            params['amount'] = self._open_order['amount'] * (self._open_order['price'] / price)
            params['type'] = 'market'
            params['side'] = 'buy'
            params['symbol'] = self.symbol

            self._close_order = super().test_order(params=params)
            if self.expose() == 0:
                self.status = CLOSED
                return 0
            return -1

        self._close_order = binance.create_market_buy_order(symbol=self.symbol, amount=self._open_order['amount'])
        self.status = WAIT_CLOSE

        time.sleep(0.5)

        # update order
        self._close_order = binance.fetch_order(id=self._close_order['id'], symbol=self.symbol)

        if self._close_order['status'] == 'open':
            self.status = WAIT_CLOSE

        if self._close_order['status'] == 'canceled':
            assert self._take_profit_order is None and self._stop_loss_order is None
            self.status = CANCELED

        if self._close_order['status'] == 'close':
            if self.expose() == 0:
                self.status = CLOSED
            else:
                self.status = ERROR

        return 0

    def secure(self, target_price, stop_loss, params):

        def protect_test(position, t_amount, t_target_price, t_stop_loss):
            position._take_profit_order = super().test_order(params={'symbol': self.symbol,
                                                                     'type': 'limit',
                                                                     'side': 'buy',
                                                                     'price': t_target_price,
                                                                     'amount': t_amount})

            position._stop_loss_order = super().test_order(params={'symbol': self.symbol,
                                                                   'type': 'limit',
                                                                   'side': 'buy',
                                                                   'price': t_stop_loss,
                                                                   'amount': t_amount})

        if not target_price <= self._open_order['price'] <= stop_loss:
            return -1

        if self._open_order is None or (self.status != WAIT_OPEN and self.status != OPEN):
            return -1

        super().secure(target_price=target_price, stop_loss=stop_loss, params=params)

        if MODE == TEST:
            protect_test(position=self, t_amount=self.pos_amount, t_target_price=target_price, t_stop_loss=stop_loss)
            self._open_order['status'] = 'closed'
            self.is_secured = True
            return 0

        # TODO - make special handling for binance errors like NoFunds etc

        take_profit_order_created = False
        stop_loss_order_created = False

        try:
            self._take_profit_order = binance.create_limit_buy_order(symbol=self.symbol, amount=self.pos_amount,
                                                                     price=target_price, params=params)
            take_profit_order_created = True
        except Exception as e:
            print("Error with placing target_price limit")
            print(e)

        try:
            self._stop_loss_order = binance.create_limit_buy_order(symbol=self.symbol, amount=self.pos_amount,
                                                                   price=stop_loss, params=params)
            stop_loss_order_created = True
        except Exception as e:
            print("Error with placing stop_loss limit")
            print(e)

        if not take_profit_order_created or not stop_loss_order_created:
            self.is_secured = False
            return -1

        self.is_secured = True
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

            if self.status == WAIT_OPEN and self._open_order and self._close_order is None:
                self.expose()
                self.status = CANCELED
                return 0

            return -1

        if self.status == WAIT_OPEN and self._open_order and self._close_order is None:

            try:
                if self.expose() != 0:
                    self.status = ERROR
                    return -1

                binance.cancel_order(id=self._open_order['id'], symbol=self.symbol)
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

            open_cost = self._open_order['cost']
            return current_price - open_cost

        assert self._close_order is not None

        open_amount = self._open_order['amount']
        closing_amount = self._close_order['amount']

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

            open_cost = self._open_order['cost']
            return 100 * ((current_price - open_cost) / open_cost)

        assert self._close_order is not None

        open_amount = self._open_order['amount']
        profit = self.get_profit(current_price=current_price)

        return 100 * (profit / open_amount)


class Scalp(Position):

    def __init__(self, pair):
        Position.__init__(self, pair=pair)
        self.long = Long(pair=pair)
        self.short = Short(pair=pair)

    def open(self, amount, upper_bound, lower_bound, date_due=None, params={}):
        pass
