import random
import unittest
from position import Long, Short
from position import Long, Short
from settings import *


class LongTest(unittest.TestCase):

    def test_init(self):

        params = {}


        with self.assertRaises(KeyError):
            pos = Long(pair='ETHUSDT', params=params)

        params['test'] = True
        params['secure'] = False
        params['amount'] = 1
        params['date due'] = None
        params['type'] = 'limit'


        # limit cant be lower than stop loss in long
        params['take profit'] = 3
        params['limit'] = 1
        params['stop loss'] = 2

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)


        # OK
        params['take profit'] = 3
        params['limit'] = 2
        params['stop loss'] = 1

        # no such instruction
        params['type'] = 'fuck'

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)


        # OK
        params['type'] = 'limit'

        # should be bool
        params['secure'] = 2

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)

        # OK
        params['secure'] = True

        # should be bool
        params['test'] = 2

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)

        params['test'] = True

        pos = Long(pair='ETHUSDT', params=params)

    def test_open(self):

        params = {'test': True,
                  'secure': False,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)

        self.assertEqual(long1.open(), 0)

        # can't after it has been opened
        with self.assertRaises(Exception):
            long1.open()

        params['type'] = 'market'
        long2 = Long(pair='ETHUSDT', params=params)

        self.assertEqual(long2.open(), 0)

        # can't after it has been opened
        with self.assertRaises(Exception):
            long2.open()

        self.assertEqual(long2.status, OPEN)

    def test_update(self):

        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)

        long1.open()

        if long1.status == WAIT_OPEN:
            orders = long1['all']
            self.assertEqual(orders['take profit'], {})
            self.assertEqual(orders['stop loss'], {})


        while long1.status == WAIT_OPEN:
            long1.update()

        orders = long1['all']
        self.assertNotEqual(orders['take profit'], {})
        self.assertNotEqual(orders['stop loss'], {})

    def test_close(self):
        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        while long1.status != OPEN:
            long1.update()

        # can't close without limit
        with self.assertRaises(ValueError):
            long1.close(close_params={})

        self.assertEqual(long1.close(limit=4), 0)
        self.assertEqual(long1.close(limit=4), -1)

        test1 = False
        test2 = False

        while not test1 or not test2:

            long2 = Long(pair='ETHUSDT', params=params)
            long2.open()

            if long2.status == WAIT_OPEN:
                res = long2.close(limit=4)

                if res == 0 and not test1:
                    # after closing waiting to open position it cancels instead
                    self.assertIn(long2.status, [CLOSED, CANCELED])
                    self.assertFalse(long2.is_secure)
                    test1 = True
                    print('canceled')
                if res == -1 and not test2:
                    # after closing waiting to open position it cancels instead
                    self.assertEqual(long2.status, OPEN)
                    test2 = True
                    print('opened')

        self.assertEqual(long1.status, CLOSED)

    def test_cancel(self):

        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        while long1.status != OPEN:
            long1.update()

        self.assertTrue(long1.is_secure)

        # cant cancel open position
        self.assertEqual(long1.cancel(), -1)
        self.assertEqual(long1.status, OPEN)

        long2 = Long(pair='ETHUSDT', params=params)
        long2.open()

        while long2.status != WAIT_OPEN:
            long2 = Long(pair='ETHUSDT', params=params)
            long2.open()

        # status is wait_open now we can cancel
        self.assertEqual(long2.cancel(), 0)
        self.assertFalse(long2.is_secure)

    def test_secure_expose(self):
        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        while long1.status != OPEN:
            long1.update()

        self.assertTrue(long1.is_secure)
        self.assertEqual(long1['stop loss']['limit'], 1)
        self.assertEqual(long1['take profit']['limit'], 3)
        self.assertEqual(long1.stop_loss_price, 1)
        self.assertEqual(long1.take_profit_price, 3)


        params['secure'] = False
        long2 = Long(pair='ETHUSDT', params=params)
        long2.open()

        self.assertFalse(long2.need_secure)
        self.assertFalse(long2.is_secure)

        while long2.status != OPEN:
            long2.update()

        long1.secure()
        long2.secure()


        self.assertTrue(long2.need_secure)
        self.assertTrue(long2.is_secure)

        self.assertEqual(long2['stop loss']['limit'], 1)
        self.assertEqual(long2['take profit']['limit'], 3)
        self.assertEqual(long1.stop_loss_price, 1)
        self.assertEqual(long1.take_profit_price, 3)

        # cant assign take profit for the same price
        self.assertEqual(long2.secure(take_profit=1.5, stop_loss=1), -1)
        self.assertEqual(long2.secure(take_profit=3, stop_loss=2.5), -1)
        self.assertEqual(long2.secure(take_profit=100, stop_loss=0.5), 0)

        self.assertEqual(long2['stop loss']['limit'], 0.5)
        self.assertEqual(long2['take profit']['limit'], 100)
        self.assertEqual(long2.stop_loss_price, 0.5)
        self.assertEqual(long2.take_profit_price, 100)

        self.assertTrue(long2.need_secure)
        self.assertTrue(long2.is_secure)

        long2.expose()

        self.assertFalse(long2.need_secure)
        self.assertFalse(long2.is_secure)

        long2.secure()
        self.assertTrue(long2.need_secure)
        self.assertTrue(long2.is_secure)
        self.assertEqual(long2['stop loss']['limit'], 0.5)
        self.assertEqual(long2['take profit']['limit'], 100)
        self.assertEqual(long2.stop_loss_price, 0.5)
        self.assertEqual(long2.take_profit_price, 100)

        long3 = Long(pair='ETHUSDT', params=params)
        long3.open()

        params['secure'] = False
        while long2.status != OPEN:
            long2.update()

        self.assertFalse(long3.need_secure)
        self.assertFalse(long3.is_secure)

        # exposing exposed position
        self.assertEqual(long3.expose(), 0)

    def test_get_fee(self):
        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        self.assertAlmostEqual(long1.get_profit(3), 0.995)
        self.assertAlmostEqual(long1.get_profit(1), -1.005)

        while long1.status != OPEN:
            long1.update()

        self.assertAlmostEqual(long1.get_fee(1), 0.003)

        long1.close(close_params={'limit': 2.5})

        self.assertAlmostEqual(long1.get_fee(), 0.0045)
        self.assertAlmostEqual(long1.get_fee(1), 0.0045)

    def test_get_profit(self):
        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        self.assertAlmostEqual(long1.get_profit(3), 0.995)
        self.assertAlmostEqual(long1.get_profit(1), -1)

        while long1.status != OPEN:
            long1.update()

        long1.close(2.5)

        self.assertAlmostEqual(long1.get_profit(3), .4955, 3)
        self.assertAlmostEqual(long1.get_profit(1), .4955, 3)

        params['amount']        = 10
        params['limit']         = 500
        params['stop loss']     = 200
        params['take profit']   = 600

        long2 = Long(pair='BTCUSDT', params=params)
        long2.open()

        while long2.status != OPEN:
            long2.update()

        long2.close(250)

        self.assertAlmostEqual(long2.get_profit(), -2507.5)

    def test_get_profit_percent(self):

        params = {'test': True,
                  'secure': True,
                  'amount': 1,
                  'date due': None,
                  'type': 'limit',
                  'take profit': 3,
                  'limit': 2,
                  'stop loss': 1}

        long1 = Long(pair='ETHUSDT', params=params)
        long1.open()

        while long1.status != OPEN:
            long1.update()

        self.assertAlmostEqual(long1.get_profit_percent(10), 399.4)

        long1.close(limit=5)
        self.assertAlmostEqual(long1.get_profit_percent(10), -25.175)