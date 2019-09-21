import random
import unittest
from book import PositionBook
from position import Long
from settings import *

params = {'test': True,
          'limit': 2,
          'stop loss': 1,
          'take profit': 3,
          'secure': True,
          'date due': None,
          'amount': 1,
          'type': 'market'}


class TestPositionBook(unittest.TestCase):

    @staticmethod
    def make_book(size):
        assert type(size) is int

        book = PositionBook(pair='ETHUSDT')
        count = 0

        for i in range(0, size, 1):

            if i % 2 == 0:
                params['type'] = 'market'


            elif i % 2 == 1:
                params['type'] = 'limit'

            pos = Long(pair='ETHUSDT', params=params)
            pos.open()

            if book._enter(position=pos) == 0:
                count += 1

        return book, count

    def test_enter(self):

        book, book_size = self.make_book(100)
        self.assertEqual(book.get_size(), book_size)

    def test_sync(self):

        book = PositionBook(pair='ETHUSDT')

        test_dict = {'test': True,
                     'price': 200}

        book, book_size = self.make_book(size=100000)

        while len(book.book[WAIT_OPEN]) > 0:
            for status, booklet in book.book.items():
                for pos_id, position in booklet.items():
                    self.assertEqual(position.status, status)

            book.sync()

    def test_fetch(self):

        book, book_size = self.make_book(size=100000)

        pos_list = []

        for status, booklet in book.book.items():
            for pos_id, position in booklet.items():
                pos_list.append(position)

        self.assertEqual(book_size, len(pos_list))

        # checking that all positions that are in the book are fetchable
        for position in pos_list:
            self.assertEqual(book.fetch_position(position.id), position)

        # checking that cant fetch wrong id
        for i in range(1, book_size):
            self.assertEqual(book.fetch_position(i), None)

    def test_size(self):

        book, init_size = self.make_book(size=1000000)

        while len(book.book[WAIT_OPEN]) != 0:
            book.sync()
            self.assertEqual(book.get_size(), init_size)

    def test_open(self):

        book = PositionBook(pair='ETHUSDT')

        # fail because test != True
        with self.assertRaises(KeyError):
            book.open(params={})

        params['limit'] = 200
        params['position'] = 'lOnG'

        # fail because no instruction or type
        with self.assertRaises(KeyError):
            book.open(params={})

        for i in range(1, 100):

            if i % 2 == 0:
                params['type'] = 'market'
                params['stop loss'] = 210
                params['take profit'] = 190

            if i % 2 == 1:
                params['type'] = 'liMit'
                params['stop loss'] = 190
                params['take profit'] = 210

            self.assertEqual(book.open(params=params), 0)

        open_positions = {**book[OPEN], **book[WAIT_OPEN]}

        for pos_id, position in open_positions.items():
            self.assertTrue(position.need_secure)

        book2 = PositionBook('ETHUSDT')
        params['secure'] = True
        params['position'] = 'LonG'

        for i in range(1, 100):

            if i % 2 == 0:
                params['type'] = 'liMit'
                params['stop loss'] = 210
                params['take profit'] = 190

            if i % 2 == 1:
                params['type'] = 'mArkET'
                params['stop loss'] = 190
                params['take profit'] = 210

            self.assertEqual(book2.open(params=params), 0)

        open_positions = {**book2[OPEN], **book2[WAIT_OPEN]}

        for pos_id, position in open_positions.items():
            self.assertTrue(position.need_secure)

    def test_get_cond(self):

        risk_tol = 90
        cond1 = lambda pos: pos.risk_factor > risk_tol
        cond2 = lambda pos: pos.risk_factor < risk_tol

        book, book_size = self.make_book(size=1500)

        cond_positions1 = book.get_cond_positions(cond1)
        cond_positions2 = book.get_cond_positions(cond2)

        for position in cond_positions1:
            self.assertGreater(position.risk_factor, risk_tol)

        for position in cond_positions2:
            self.assertLess(position.risk_factor, risk_tol)

        cond3 = lambda pos: pos.risk_factor < risk_tol and pos.status == OPEN

        cond_positions3 = book.get_cond_positions(cond3, OPEN)
        cond_positions4 = book.get_cond_positions(cond3)

        self.assertEqual(cond_positions3, cond_positions4)

        book2 = PositionBook('ETHUSDT')

        # 1
        book2.open(params={'test': True,
                           'position': 'lonG',
                           'type': 'Limit',
                           'limit': 190,
                           'take profit': 230,
                           'stop loss': 150,
                           'secure': True,
                           'date due': None,
                           'amount': 2})

        # 2
        book2.open(params={'test': True,
                           'position': 'long',
                           'type': 'Limit',
                           'limit': 200,
                           'take profit': 150,
                           'stop loss': 250,
                           'secure': False,
                           'date due': None,
                           'amount': 4})

        # 3
        book2.open(params={'test': True,
                           'position': 'long',
                           'type': 'market',
                           'limit': 130,
                           'take profit': 100,
                           'stop loss': 150,
                           'secure': False,
                           'date due': None,
                           'amount': 0.7})

        # should be len 2
        list1 = book2.get_cond_positions(cond=lambda pos: isinstance(pos, Long))
        list2 = book2.get_cond_positions(cond=lambda pos: pos['open']['limit'] > 140)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 2)

        # should be len 1
        list3 = book2.get_cond_positions(cond=lambda pos: pos.need_secure and pos.take_profit_price > 200)
        self.assertEqual(len(list3), 1)

        # should be 0
        list4 = book2.get_cond_positions(cond=lambda pos: not pos.need_secure and pos.take_profit_price > 200)
        self.assertEqual(len(list4), 0)

    def test_close_cond(self):

        book, book_size = self.make_book(size=100000)

        limit_pos = book.get_cond_positions(cond=lambda pos: pos.params['type'] == 'limit')
        num_limit = len(limit_pos)

        book.close_cond(cond=lambda pos: pos.params['type'] == 'limit', close_price=3)

        self.assertEqual(book_size - num_limit, len(book[OPEN]) + len(book[WAIT_OPEN]))
        self.assertEqual(num_limit, len(book[CLOSED]) + len(book[CANCELED]))

        prev_closed_size = len(book[CLOSED])
        book.close_cond(cond=lambda pos: pos.id < 1000000, close_price=3)

        # supposed to be the same because ids are distributed from 1m to 9m
        self.assertEqual(prev_closed_size, len(book[CLOSED]))

        remaining_limit = book.get_cond_positions(cond=lambda pos: pos.params['type'] == 'limit', status=OPEN) + \
                          book.get_cond_positions(cond=lambda pos: pos.params['type'] == 'limit', status=WAIT_OPEN)

        # should be empty because we closed all
        self.assertEqual([], remaining_limit)

        unclosed = -book.close_cond(cond=lambda pos: pos.id > 9000000, close_price=4)

        if unclosed != 0:
            print("number of unclosed positions is {}".format(unclosed))

        first_closed = book.get_cond_positions(cond=lambda pos: pos['close']['limit'] == 3)
        second_closed = book.get_cond_positions(cond=lambda pos: pos['close']['limit'] == 4)

        self.assertEqual(len(book[CLOSED]), len(first_closed + second_closed))

