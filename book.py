from settings import *
from position import Position, Long, Short, Scalp
import asyncio
import numpy as np


class PositionBook(object):

    def __init__(self, pair):

        self.pair = pair
        self.symbol = binance_coins[pair]

        self.book = {WAIT_OPEN: {},
                     OPEN: {},
                     CLOSED: {},
                     CANCELED: {}}

    def fetch_position(self, pos_id):

        position = None

        for key, booklet in self.book.items():
            try:
                position = booklet[pos_id]

            except:
                pass

        return position

    def sync(self):
        """
        goal is ->  position is in category <=> position is in the exchange with corresponding credentials
        :return: void
        """

        new_book = {}
        update_list = [self.book[WAIT_OPEN], self.book[OPEN]]

        for status, booklet in self.book.items():
            new_book[status] = {}

        for status, booklet in self.book.items():
            for pos_id, position in booklet.items():

                position.update()
                new_status = position.status

                if status == new_status:
                    new_book[status][pos_id] = position
                else:
                    new_book[new_status][pos_id] = position

        self.book = new_book

    def open(self, params={}):

        """
        :param params: MUST contain:
                                    1. type (one of the Positions' instances) -> str
                                    2. instruction (limit, market, etc) -> str

        :return: 0 on success
                -1 on failure
        """

        if 'position' not in params:
            raise KeyError

        pos_type = params['position'].lower()

        if type(pos_type) is not str or pos_type not in position_types:
            return -1


        new_pos = None

        if pos_type == 'long':
            new_pos = Long(pair=self.pair, params=params)

        if pos_type == 'short':
            # TODO - add after finishing short
            pass

        if pos_type == 'scalp':
            # TODO - add after finishing scalp
            pass
        

        if new_pos is None or new_pos.open() != 0:
            return -1

        return self._enter(position=new_pos)

    def close(self, pos_id, **kwargs):

        position = self.fetch_position(pos_id=pos_id)

        if position is None:
            return -1

        res = position.close(kwargs)

        if res != 0:
            return -1

        return 0

    def close_cond(self, cond, close_price=None, status=None):

        """
        closing open positions and canceling wait_open positions
        :param close_price: a non negative float or int
        :param status: WAIT_OPEN, OPEN
        :param cond: gets position and returns boolean
        :return: 0 on success -# on failure # is the number of unclosed positions with this cond
        """

        if type(close_price) not in [int, float] or close_price < 0:
            raise ValueError('closing price has to be a non negative number')

        if status not in [OPEN, WAIT_OPEN, None]:
            raise KeyError("no status {} exists in book".format(status))

        pos_list = []

        if status == OPEN:
            pos_list = self.get_cond_positions(cond=cond, status=OPEN)

        elif status == WAIT_OPEN:
            pos_list = self.get_cond_positions(cond=cond, status=WAIT_OPEN)

        elif status is None:

            open_pos_list = self.get_cond_positions(cond=cond, status=OPEN)
            wait_open_pos_list = self.get_cond_positions(cond=cond, status=WAIT_OPEN)
            pos_list = open_pos_list + wait_open_pos_list

        return self._close_list(pos_list=pos_list, close_price=close_price)

    def _enter(self, position):

        if not isinstance(position, Position):
            return -1

        if position.pair != self.pair:
            return -1

        position.update()

        if self.fetch_position(pos_id=position.id) is not None:
            return -1

        self.book[position.status][position.id] = position

        return position.id

    def _close_list(self, pos_list, close_price):

        if type(pos_list) is not list:
            return 0

        not_closed = []

        # timeout control
        iteration = 0

        initial_size = len(pos_list)

        while len(pos_list) != 0 and iteration < 100:

            for position in pos_list:

                if not isinstance(position, Position):
                    continue

                if position.close(close_price=close_price) != 0:
                    not_closed.append(position)

            pos_list = not_closed
            not_closed = []
            iteration += 1

        self.sync()

        # always non-positive number
        return len(not_closed) - len(pos_list)

    def get_size(self):

        sum = 0
        for key, booklet in self.book.items():
            sum += len(booklet)

        return sum

    def get_cond_positions(self, cond, status=None):

        position_base = {}
        cond_positions = []



        try:
            position_base = self.book[status]

        except:
            for status, booklet in self.book.items():
                position_base = {**position_base, **booklet}

        for pos_id, position in position_base.items():
            try:
                if cond(position):
                    cond_positions.append(position)
            except:
                pass

        return cond_positions


    def __getitem__(self, status):

        try:
            return self.book[status]

        except:
            return self.book[OPEN]

    @staticmethod
    def move_to(key, src, dest):
        if type(src) != dict or type(dest) != dict:
            return -1

        try:
            tmp = src[key]
            del src[key]
            dest[key] = tmp
        except Exception as e:
            print(e)

        return 0
