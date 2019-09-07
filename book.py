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

        try:

            if MODE == TEST:
                assert params['test']

            position_type = params['type']
            instruction   = params['instruction']

            position_type = position_type.lower()
            instruction = instruction.lower()

            if type(position_type) is not str or type(instruction) is not str:
                return -1

            if position_type not in position_types:
                return -1

            if instruction not in position_instructions:
                return -1

            amount          = params['amount']
            limit           = 0
            target_price    = params['target price']
            stop_loss       = params['stop loss']
            secured         = params['secured']
            date_due        = params['date due']

            if instruction == 'limit':
                limit = params['limit']

        except Exception as e:
            print(e)
            return -1


        # FIRST STEP

        position = Position(pair=self.pair)

        if position_type == 'long':
            position = Long(pair=self.pair)

        elif position_type == 'short':
            position = Short(pair=self.pair)

        elif position_type == 'scalp':
            position = Scalp(pair=self.pair)


        # SECOND STEP

        res = -1

        if instruction == 'limit':
            res = position.open_limit(amount=amount,
                                      limit=limit,
                                      target_price=target_price,
                                      stop_loss=stop_loss,
                                      secured=secured,
                                      date_due=date_due,
                                      params=params)

        if instruction == 'market':
            res = position.open_market(amount=amount,
                                       target_price=target_price,
                                       stop_loss=stop_loss,
                                       secured=secured,
                                       date_due=date_due,
                                       params=params)

        if res != 0:
            return -1

        if self._enter(position=position) != 0:
            return -1

        return 0

    def close(self, pos_id, params={}):

        position = self.fetch_position(pos_id=pos_id)

        if position is None:
            return -1

        res = position.close(params=params)

        if res != 0:
            return -1

        return 0


    def _enter(self, position):

        if not isinstance(position, Position):
            return -1

        if position.pair != self.pair:
            return -1

        position.update()

        if self.fetch_position(pos_id=position.id) is not None:
            return -1

        self.book[position.status][position.id] = position

        return 0

    @staticmethod
    def _close_list(pos_list):

        if type(pos_list) is not list:
            return -1

        not_closed = []

        # timeout control
        iteration = 0

        while len(pos_list) != 0 and iteration < 100:

            for position in pos_list:

                if not isinstance(position, Position):
                    continue

                if position.close() != 0:
                    not_closed.append(position)

            pos_list = not_closed
            not_closed = []
            iteration += 1

        if len(not_closed) > 0:
            return -1

        return 0


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
            if cond(position):
                cond_positions.append(position)

        return cond_positions

    def close_cond(self, cond):

        """
        closing open positions and canceling wait_open positions
        :param cond: gets position and returns boolean
        :return: 0 on success -1 on failure
        """

        open_pos_list = self.get_cond_positions(cond=cond, status=OPEN)
        wait_open_pos_list = self.get_cond_positions(cond=cond, status=WAIT_OPEN)

        pos_list = open_pos_list.extend(wait_open_pos_list)

        if self._close_list(pos_list=pos_list) != 0:
            return -1

        return 0


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
