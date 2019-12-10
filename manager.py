
from book import PositionBook
from position import Position
from config import *

class PositionManager:

    def __init__(self, pair):

        self.pair = pair
        self.symbol = binance_coins[pair]

        self.book = PositionBook(pair=self.pair)


    def open(self, params={}):

        """
        :param params: MUST contain:
                                    1. type (one of the Positions' instances) -> str
                                    2. instruction (limit, market, etc) -> str

        :return: 0 on success
                -1 on failure
        """

        if MODE == TEST:
            assert params['test']

        try:
            position_type = params['type']
            instruction   = params['instruction']

            position_type.lower()
            instruction.lower()

            if type(position_type) is not str or type(instruction) is not str:
                return -1



        except:
            return -1


class AssetManager:

    def __init__(self, pair, base, quote, decision_method):

        self.pair = pair
        self.symbol = binance_coins[pair]

        whole_pair = self.symbol.split('/')
        self.base = whole_pair[0]
        self.quote = whole_pair[1]

        self.pos_book = PositionBook(pair=pair)
