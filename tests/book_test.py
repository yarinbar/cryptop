import random
import unittest
from book import PositionBook
from position import Long, Short
from settings import *

test_dict = {'test': True,
             'price': 200}

class TestPositionBook(unittest.TestCase):

    @staticmethod
    def make_book(size):
        assert type(size) is int

        book = PositionBook(pair='ETHUSDT')
        count = 0

        for i in range(0, size, 1):

            pos = None

            if i % 4 == 0:
                pos = Long(pair='ETHUSDT')
                pos.open_market(amount=1, target_price=210, stop_loss=190, params=test_dict)

            elif i % 4 == 1:
                pos = Short(pair='ETHUSDT')
                pos.open_market(amount=1, target_price=190, stop_loss=210, params=test_dict)

            elif i % 4 == 2:
                pos = Long(pair='ETHUSDT')
                pos.open_limit(amount=1, limit=200, target_price=210, stop_loss=190, params=test_dict)

            elif i % 4 == 3:
                pos = Short(pair='ETHUSDT')
                pos.open_limit(amount=1, limit=200, target_price=190, stop_loss=210, params=test_dict)

            if book._enter(position=pos) == 0:
                count += 1

        return book, count

    def test_enter(self):

        book, book_size = self.make_book(100)

        self.assertEqual(first=book.get_size(), second=book_size)


        pos1 = Long(pair='ETHUSDT')
        pos1.open_market(amount=1, target_price=210, stop_loss=190, params=test_dict)

        pos2 = Long(pair='ETHUSDT')
        pos2.open_market(amount=1, target_price=210, stop_loss=190, params=test_dict)

        pos2.id = pos1.id

        book.enter(pos1)
        book.enter(pos2)
        book.enter(3)

        self.assertEqual(book.get_size(), book_size + 1)

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
        self.assertEqual(book.open(params={}), -1)

        params = {'test': True,
                  'price': 200,
                  'secured': False,
                  'amount': 1,
                  'date due': None}

        # fail because no instruction or type
        self.assertEqual(book.open(params={}), -1)


        for i in range(1, 1000):

            if i % 2 == 0:
                params['type'] = 'ShoRt'
                params['stop loss'] = 210
                params['target price'] = 190

            if i % 2 == 1:
                params['type'] = 'LonG'
                params['stop loss'] = 190
                params['target price'] = 210


            if i % 3 == 0:
                params['instruction'] = 'marKet'
            else:
                params['instruction'] = 'lImiT'
                params['limit'] = 200

            self.assertEqual(book.open(params=params), 0)



        open_positions = {**book[OPEN], **book[WAIT_OPEN]}

        for pos_id, position in open_positions.items():
            self.assertFalse(position.need_secure)


        book2 = PositionBook('ETHUSDT')
        params['secured'] = True

        for i in range(1, 1000):

            if i % 2 == 0:
                params['type'] = 'ShoRt'
                params['stop loss'] = 210
                params['target price'] = 190

            if i % 2 == 1:
                params['type'] = 'LonG'
                params['stop loss'] = 190
                params['target price'] = 210


            if i % 3 == 0:
                params['instruction'] = 'marKet'
            else:
                params['instruction'] = 'lImiT'
                params['limit'] = 200

            self.assertEqual(book2.open(params=params), 0)



        open_positions = {**book2[OPEN], **book2[WAIT_OPEN]}

        for pos_id, position in open_positions.items():
            self.assertTrue(position.need_secure)

    def test_get_cond(self):

        risk_tol = 90
        cond1 = lambda pos: pos.risk_factor > risk_tol
        cond2 = lambda pos: pos.risk_factor < risk_tol

        book, book_size = self.make_book(size=1500)

        cond_positions1 = book.get_cond(cond1)
        cond_positions2 = book.get_cond(cond2)

        for position in cond_positions1:
            self.assertGreater(position.risk_factor, risk_tol)

        for position in cond_positions2:
            self.assertLess(position.risk_factor, risk_tol)

        cond3 = lambda pos: pos.risk_factor < risk_tol and pos.status == OPEN

        cond_positions3 = book.get_cond(cond3, OPEN)
        cond_positions4 = book.get_cond(cond3)

        self.assertEqual(cond_positions3, cond_positions4)

        book2 = PositionBook('ETHUSDT')

        #1
        book2.open(params={'test': True,
                           'type': 'lonG',
                           'instruction': 'Limit',
                           'limit': 190,
                           'target price': 230,
                           'stop loss': 150,
                           'secured': True,
                           'date due': None,
                           'amount': 2})

        #2
        book2.open(params={'test': True,
                           'type': 'short',
                           'instruction': 'Limit',
                           'limit': 200,
                           'target price': 150,
                           'stop loss': 250,
                           'secured': False,
                           'date due': None,
                           'amount': 4})

        #3
        book2.open(params={'test': True,
                           'type': 'short',
                           'instruction': 'market',
                           'price': 130,
                           'target price': 100,
                           'stop loss': 150,
                           'secured': False,
                           'date due': None,
                           'amount': 0.7})

        # should be len 2
        list1 = book2.get_cond(cond=lambda pos: isinstance(pos, Short))
        list2 = book2.get_cond(cond=lambda pos: pos['open']['price'] > 140)

        self.assertEqual(len(list1), 2)
        self.assertEqual(len(list2), 2)

        # should be len 1
        list3 = book2.get_cond(cond=lambda pos: pos.need_secure and pos.target_price > 200)
        self.assertEqual(len(list3), 1)

        # should be 0
        list4 = book2.get_cond(cond=lambda pos: not pos.need_secure and pos.target_price > 200)
        self.assertEqual(len(list4), 0)