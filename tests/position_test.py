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
        params['secured'] = False
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
        params['secured'] = 2

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)

        # OK
        params['secured'] = True

        # should be bool
        params['test'] = 2

        with self.assertRaises(ValueError):
            pos = Long(pair='ETHUSDT', params=params)

        params['test'] = True

        pos = Long(pair='ETHUSDT', params=params)

    def test_open(self):

        params = {'test': True,
                  'secured': False,
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
