from os import environ, path
import logging
from binance.enums import *
import sched
import time
import ccxt

scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)
TEST = 0
RUN = 1

"""
CHANGEABLE SETTINGS
"""

MODE = TEST

COINS = {'ETH': 'ETH',
         'BTC': 'BTC',
         'USDT': 'USDT'}

POSITION_LIMIT = 100

position_types = {'long': 'long',
                  'short': 'short',
                  'scalp': 'scalp'}

position_instructions = {'limit': 'limit',
                         'market': 'market'}

MAKER_FEE = 0.1 / 100
TAKER_FEE = 0.1 / 100

# times to update within candle timespan (X times in each candle)
UPDATES_FREQ = 50

# how many samples to save for validation
VAL_SIZE = 4096


"""
END CHANGEABLE SETTINGS
"""


WORK_DIR = path.dirname(__file__)

LOG_DIR     = path.join(WORK_DIR, 'logs')
DATA_DIR    = path.join(WORK_DIR, 'data')
DS_DIR      = path.join(WORK_DIR, 'datasets')
MODEL_DIR   = path.join(WORK_DIR, 'models')
BACKUP_DIR  = path.join(WORK_DIR, 'backups')




EMPTY       = 0
WAIT_OPEN   = 1
OPEN        = 2
WAIT_CLOSE  = 3
CLOSED      = 4
CANCELED    = 5
ERROR       = 6

API_KEY    = environ.get('BINANCE_API_KEY')
API_SECRET = environ.get('BINANCE_API_SECRET')

CLIENT_INTERVALS = {'1m':  KLINE_INTERVAL_1MINUTE,
                    '5m':  KLINE_INTERVAL_5MINUTE,
                    '15m': KLINE_INTERVAL_15MINUTE,
                    '30m': KLINE_INTERVAL_30MINUTE,
                    '1h':  KLINE_INTERVAL_1HOUR,
                    '2h':  KLINE_INTERVAL_2HOUR,
                    '4h':  KLINE_INTERVAL_4HOUR,
                    '6h':  KLINE_INTERVAL_6HOUR,
                    '12h': KLINE_INTERVAL_12HOUR,
                    '1d':  KLINE_INTERVAL_1DAY,
                    '3d':  KLINE_INTERVAL_3DAY,
                    '1w':  KLINE_INTERVAL_1WEEK}

binance_class = getattr(ccxt, 'binance')
binance = binance_class({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'timeout': 3000,
    'enableRateLimit': True,
    'adjustForTimeDifference': True
})

SELL = -1
HOLD = 0
BUY = 1

interval_milli = {'1m': 1 * 60 * 1000,
                  '5m': 2 * 60 * 1000,
                  '15m': 15 * 60 * 1000,
                  '30m': 30 * 60 * 1000,
                  '1h': 1 * 60 * 60 * 1000,
                  '2h': 2 * 60 * 60 * 1000,
                  '4h': 4 * 60 * 60 * 1000,
                  '6h': 6 * 60 * 60 * 1000,
                  '8h': 8 * 60 * 60 * 1000,
                  '12h': 12 * 60 * 60 * 1000,
                  '1d': 1 * 24 * 60 * 60 * 1000,
                  '3d': 3 * 24 * 60 * 60 * 1000,
                  '1w': 7 * 24 * 60 * 60 * 1000}

interval_secs = {'1m': 1 * 60,
                 '5m': 2 * 60,
                 '15m': 15 * 60,
                 '30m': 30 * 60,
                 '1h': 1 * 60 * 60,
                 '2h': 2 * 60 * 60,
                 '4h': 4 * 60 * 60,
                 '6h': 6 * 60 * 60,
                 '8h': 8 * 60 * 60,
                 '12h': 12 * 60 * 60,
                 '1d': 1 * 24 * 60 * 60,
                 '3d': 3 * 24 * 60 * 60,
                 '1w': 7 * 24 * 60 * 60}

'''
exception handler modes
'''
ABORT = 0
SELL_OPEN = 1

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename=r'C:\Users\Yarin\Documents\Yarin\Crypto\Trading_Bot\bot_v2\bot_log.log', level=logging.INFO,
                    format=LOG_FORMAT, filemode='w')
bot_log = logging.getLogger(name='bot_log.log')

binance_coins = {'ETHBTC': 'ETH/BTC',
                 'LTCBTC': 'LTC/BTC',
                 'BNBBTC': 'BNB/BTC',
                 'NEOBTC': 'NEO/BTC',
                 'QTUMETH': 'QTUM/ETH',
                 'EOSETH': 'EOS/ETH',
                 'SNTETH': 'SNT/ETH',
                 'BNTETH': 'BNT/ETH',
                 'BCCBTC': 'BCC/BTC',
                 'GASBTC': 'GAS/BTC',
                 'BNBETH': 'BNB/ETH',
                 'BTCUSDT': 'BTC/USDT',
                 'ETHUSDT': 'ETH/USDT',
                 'HSRBTC': 'HSR/BTC',
                 'OAXETH': 'OAX/ETH',
                 'DNTETH': 'DNT/ETH',
                 'MCOETH': 'MCO/ETH',
                 'ICNETH': 'ICN/ETH',
                 'MCOBTC': 'MCO/BTC',
                 'WTCBTC': 'WTC/BTC',
                 'WTCETH': 'WTC/ETH',
                 'LRCBTC': 'LRC/BTC',
                 'LRCETH': 'LRC/ETH',
                 'QTUMBTC': 'QTUM/BTC',
                 'YOYOBTC': 'YOYOW/BTC',
                 'OMGBTC': 'OMG/BTC',
                 'OMGETH': 'OMG/ETH',
                 'ZRXBTC': 'ZRX/BTC',
                 'ZRXETH': 'ZRX/ETH',
                 'STRATBTC': 'STRAT/BTC',
                 'STRATETH': 'STRAT/ETH',
                 'SNGLSBTC': 'SNGLS/BTC',
                 'SNGLSETH': 'SNGLS/ETH',
                 'BQXBTC': 'BQX/BTC',
                 'BQXETH': 'BQX/ETH',
                 'KNCBTC': 'KNC/BTC',
                 'KNCETH': 'KNC/ETH',
                 'FUNBTC': 'FUN/BTC',
                 'FUNETH': 'FUN/ETH',
                 'SNMBTC': 'SNM/BTC',
                 'SNMETH': 'SNM/ETH',
                 'NEOETH': 'NEO/ETH',
                 'IOTABTC': 'IOTA/BTC',
                 'IOTAETH': 'IOTA/ETH',
                 'LINKBTC': 'LINK/BTC',
                 'LINKETH': 'LINK/ETH',
                 'XVGBTC': 'XVG/BTC',
                 'XVGETH': 'XVG/ETH',
                 'SALTBTC': 'SALT/BTC',
                 'SALTETH': 'SALT/ETH',
                 'MDABTC': 'MDA/BTC',
                 'MDAETH': 'MDA/ETH',
                 'MTLBTC': 'MTL/BTC',
                 'MTLETH': 'MTL/ETH',
                 'SUBBTC': 'SUB/BTC',
                 'SUBETH': 'SUB/ETH',
                 'EOSBTC': 'EOS/BTC',
                 'SNTBTC': 'SNT/BTC',
                 'ETCETH': 'ETC/ETH',
                 'ETCBTC': 'ETC/BTC',
                 'MTHBTC': 'MTH/BTC',
                 'MTHETH': 'MTH/ETH',
                 'ENGBTC': 'ENG/BTC',
                 'ENGETH': 'ENG/ETH',
                 'DNTBTC': 'DNT/BTC',
                 'ZECBTC': 'ZEC/BTC',
                 'ZECETH': 'ZEC/ETH',
                 'BNTBTC': 'BNT/BTC',
                 'ASTBTC': 'AST/BTC',
                 'ASTETH': 'AST/ETH',
                 'DASHBTC': 'DASH/BTC',
                 'DASHETH': 'DASH/ETH',
                 'OAXBTC': 'OAX/BTC',
                 'ICNBTC': 'ICN/BTC',
                 'BTGBTC': 'BTG/BTC',
                 'BTGETH': 'BTG/ETH',
                 'EVXBTC': 'EVX/BTC',
                 'EVXETH': 'EVX/ETH',
                 'REQBTC': 'REQ/BTC',
                 'REQETH': 'REQ/ETH',
                 'VIBBTC': 'VIB/BTC',
                 'VIBETH': 'VIB/ETH',
                 'HSRETH': 'HSR/ETH',
                 'TRXBTC': 'TRX/BTC',
                 'TRXETH': 'TRX/ETH',
                 'POWRBTC': 'POWR/BTC',
                 'POWRETH': 'POWR/ETH',
                 'ARKBTC': 'ARK/BTC',
                 'ARKETH': 'ARK/ETH',
                 'YOYOETH': 'YOYOW/ETH',
                 'XRPBTC': 'XRP/BTC',
                 'XRPETH': 'XRP/ETH',
                 'MODBTC': 'MOD/BTC',
                 'MODETH': 'MOD/ETH',
                 'ENJBTC': 'ENJ/BTC',
                 'ENJETH': 'ENJ/ETH',
                 'STORJBTC': 'STORJ/BTC',
                 'STORJETH': 'STORJ/ETH',
                 'BNBUSDT': 'BNB/USDT',
                 'VENBNB': 'VEN/BNB',
                 'YOYOBNB': 'YOYOW/BNB',
                 'POWRBNB': 'POWR/BNB',
                 'VENBTC': 'VEN/BTC',
                 'VENETH': 'VEN/ETH',
                 'KMDBTC': 'KMD/BTC',
                 'KMDETH': 'KMD/ETH',
                 'NULSBNB': 'NULS/BNB',
                 'RCNBTC': 'RCN/BTC',
                 'RCNETH': 'RCN/ETH',
                 'RCNBNB': 'RCN/BNB',
                 'NULSBTC': 'NULS/BTC',
                 'NULSETH': 'NULS/ETH',
                 'RDNBTC': 'RDN/BTC',
                 'RDNETH': 'RDN/ETH',
                 'RDNBNB': 'RDN/BNB',
                 'XMRBTC': 'XMR/BTC',
                 'XMRETH': 'XMR/ETH',
                 'DLTBNB': 'DLT/BNB',
                 'WTCBNB': 'WTC/BNB',
                 'DLTBTC': 'DLT/BTC',
                 'DLTETH': 'DLT/ETH',
                 'AMBBTC': 'AMB/BTC',
                 'AMBETH': 'AMB/ETH',
                 'AMBBNB': 'AMB/BNB',
                 'BCCETH': 'BCC/ETH',
                 'BCCUSDT': 'BCC/USDT',
                 'BCCBNB': 'BCC/BNB',
                 'BATBTC': 'BAT/BTC',
                 'BATETH': 'BAT/ETH',
                 'BATBNB': 'BAT/BNB',
                 'BCPTBTC': 'BCPT/BTC',
                 'BCPTETH': 'BCPT/ETH',
                 'BCPTBNB': 'BCPT/BNB',
                 'ARNBTC': 'ARN/BTC',
                 'ARNETH': 'ARN/ETH',
                 'GVTBTC': 'GVT/BTC',
                 'GVTETH': 'GVT/ETH',
                 'CDTBTC': 'CDT/BTC',
                 'CDTETH': 'CDT/ETH',
                 'GXSBTC': 'GXS/BTC',
                 'GXSETH': 'GXS/ETH',
                 'NEOUSDT': 'NEO/USDT',
                 'NEOBNB': 'NEO/BNB',
                 'POEBTC': 'POE/BTC',
                 'POEETH': 'POE/ETH',
                 'QSPBTC': 'QSP/BTC',
                 'QSPETH': 'QSP/ETH',
                 'QSPBNB': 'QSP/BNB',
                 'BTSBTC': 'BTS/BTC',
                 'BTSETH': 'BTS/ETH',
                 'BTSBNB': 'BTS/BNB',
                 'XZCBTC': 'XZC/BTC',
                 'XZCETH': 'XZC/ETH',
                 'XZCBNB': 'XZC/BNB',
                 'LSKBTC': 'LSK/BTC',
                 'LSKETH': 'LSK/ETH',
                 'LSKBNB': 'LSK/BNB',
                 'TNTBTC': 'TNT/BTC',
                 'TNTETH': 'TNT/ETH',
                 'FUELBTC': 'FUEL/BTC',
                 'FUELETH': 'FUEL/ETH',
                 'MANABTC': 'MANA/BTC',
                 'MANAETH': 'MANA/ETH',
                 'BCDBTC': 'BCD/BTC',
                 'BCDETH': 'BCD/ETH',
                 'DGDBTC': 'DGD/BTC',
                 'DGDETH': 'DGD/ETH',
                 'IOTABNB': 'IOTA/BNB',
                 'ADXBTC': 'ADX/BTC',
                 'ADXETH': 'ADX/ETH',
                 'ADXBNB': 'ADX/BNB',
                 'ADABTC': 'ADA/BTC',
                 'ADAETH': 'ADA/ETH',
                 'PPTBTC': 'PPT/BTC',
                 'PPTETH': 'PPT/ETH',
                 'CMTBTC': 'CMT/BTC',
                 'CMTETH': 'CMT/ETH',
                 'CMTBNB': 'CMT/BNB',
                 'XLMBTC': 'XLM/BTC',
                 'XLMETH': 'XLM/ETH',
                 'XLMBNB': 'XLM/BNB',
                 'CNDBTC': 'CND/BTC',
                 'CNDETH': 'CND/ETH',
                 'CNDBNB': 'CND/BNB',
                 'LENDBTC': 'LEND/BTC',
                 'LENDETH': 'LEND/ETH',
                 'WABIBTC': 'WABI/BTC',
                 'WABIETH': 'WABI/ETH',
                 'WABIBNB': 'WABI/BNB',
                 'LTCETH': 'LTC/ETH',
                 'LTCUSDT': 'LTC/USDT',
                 'LTCBNB': 'LTC/BNB',
                 'TNBBTC': 'TNB/BTC',
                 'TNBETH': 'TNB/ETH',
                 'WAVESBTC': 'WAVES/BTC',
                 'WAVESETH': 'WAVES/ETH',
                 'WAVESBNB': 'WAVES/BNB',
                 'GTOBTC': 'GTO/BTC',
                 'GTOETH': 'GTO/ETH',
                 'GTOBNB': 'GTO/BNB',
                 'ICXBTC': 'ICX/BTC',
                 'ICXETH': 'ICX/ETH',
                 'ICXBNB': 'ICX/BNB',
                 'OSTBTC': 'OST/BTC',
                 'OSTETH': 'OST/ETH',
                 'OSTBNB': 'OST/BNB',
                 'ELFBTC': 'ELF/BTC',
                 'ELFETH': 'ELF/ETH',
                 'AIONBTC': 'AION/BTC',
                 'AIONETH': 'AION/ETH',
                 'AIONBNB': 'AION/BNB',
                 'NEBLBTC': 'NEBL/BTC',
                 'NEBLETH': 'NEBL/ETH',
                 'NEBLBNB': 'NEBL/BNB',
                 'BRDBTC': 'BRD/BTC',
                 'BRDETH': 'BRD/ETH',
                 'BRDBNB': 'BRD/BNB',
                 'MCOBNB': 'MCO/BNB',
                 'EDOBTC': 'EDO/BTC',
                 'EDOETH': 'EDO/ETH',
                 'WINGSBTC': 'WINGS/BTC',
                 'WINGSETH': 'WINGS/ETH',
                 'NAVBTC': 'NAV/BTC',
                 'NAVETH': 'NAV/ETH',
                 'NAVBNB': 'NAV/BNB',
                 'LUNBTC': 'LUN/BTC',
                 'LUNETH': 'LUN/ETH',
                 'TRIGBTC': 'TRIG/BTC',
                 'TRIGETH': 'TRIG/ETH',
                 'TRIGBNB': 'TRIG/BNB',
                 'APPCBTC': 'APPC/BTC',
                 'APPCETH': 'APPC/ETH',
                 'APPCBNB': 'APPC/BNB',
                 'VIBEBTC': 'VIBE/BTC',
                 'VIBEETH': 'VIBE/ETH',
                 'RLCBTC': 'RLC/BTC',
                 'RLCETH': 'RLC/ETH',
                 'RLCBNB': 'RLC/BNB',
                 'INSBTC': 'INS/BTC',
                 'INSETH': 'INS/ETH',
                 'PIVXBTC': 'PIVX/BTC',
                 'PIVXETH': 'PIVX/ETH',
                 'PIVXBNB': 'PIVX/BNB',
                 'IOSTBTC': 'IOST/BTC',
                 'IOSTETH': 'IOST/ETH',
                 'CHATBTC': 'CHAT/BTC',
                 'CHATETH': 'CHAT/ETH',
                 'STEEMBTC': 'STEEM/BTC',
                 'STEEMETH': 'STEEM/ETH',
                 'STEEMBNB': 'STEEM/BNB',
                 'NANOBTC': 'NANO/BTC',
                 'NANOETH': 'NANO/ETH',
                 'NANOBNB': 'NANO/BNB',
                 'VIABTC': 'VIA/BTC',
                 'VIAETH': 'VIA/ETH',
                 'VIABNB': 'VIA/BNB',
                 'BLZBTC': 'BLZ/BTC',
                 'BLZETH': 'BLZ/ETH',
                 'BLZBNB': 'BLZ/BNB',
                 'AEBTC': 'AE/BTC',
                 'AEETH': 'AE/ETH',
                 'AEBNB': 'AE/BNB',
                 'RPXBTC': 'RPX/BTC',
                 'RPXETH': 'RPX/ETH',
                 'RPXBNB': 'RPX/BNB',
                 'NCASHBTC': 'NCASH/BTC',
                 'NCASHETH': 'NCASH/ETH',
                 'NCASHBNB': 'NCASH/BNB',
                 'POABTC': 'POA/BTC',
                 'POAETH': 'POA/ETH',
                 'POABNB': 'POA/BNB',
                 'ZILBTC': 'ZIL/BTC',
                 'ZILETH': 'ZIL/ETH',
                 'ZILBNB': 'ZIL/BNB',
                 'ONTBTC': 'ONT/BTC',
                 'ONTETH': 'ONT/ETH',
                 'ONTBNB': 'ONT/BNB',
                 'STORMBTC': 'STORM/BTC',
                 'STORMETH': 'STORM/ETH',
                 'STORMBNB': 'STORM/BNB',
                 'QTUMBNB': 'QTUM/BNB',
                 'QTUMUSDT': 'QTUM/USDT',
                 'XEMBTC': 'XEM/BTC',
                 'XEMETH': 'XEM/ETH',
                 'XEMBNB': 'XEM/BNB',
                 'WANBTC': 'WAN/BTC',
                 'WANETH': 'WAN/ETH',
                 'WANBNB': 'WAN/BNB',
                 'WPRBTC': 'WPR/BTC',
                 'WPRETH': 'WPR/ETH',
                 'QLCBTC': 'QLC/BTC',
                 'QLCETH': 'QLC/ETH',
                 'SYSBTC': 'SYS/BTC',
                 'SYSETH': 'SYS/ETH',
                 'SYSBNB': 'SYS/BNB',
                 'QLCBNB': 'QLC/BNB',
                 'GRSBTC': 'GRS/BTC',
                 'GRSETH': 'GRS/ETH',
                 'ADAUSDT': 'ADA/USDT',
                 'ADABNB': 'ADA/BNB',
                 'CLOAKBTC': 'CLOAK/BTC',
                 'CLOAKETH': 'CLOAK/ETH',
                 'GNTBTC': 'GNT/BTC',
                 'GNTETH': 'GNT/ETH',
                 'GNTBNB': 'GNT/BNB',
                 'LOOMBTC': 'LOOM/BTC',
                 'LOOMETH': 'LOOM/ETH',
                 'LOOMBNB': 'LOOM/BNB',
                 'XRPUSDT': 'XRP/USDT',
                 'BCNBTC': 'BCN/BTC',
                 'BCNETH': 'BCN/ETH',
                 'BCNBNB': 'BCN/BNB',
                 'REPBTC': 'REP/BTC',
                 'REPETH': 'REP/ETH',
                 'REPBNB': 'REP/BNB',
                 'BTCTUSD': 'BTC/TUSD',
                 'TUSDBTC': 'TUSD/BTC',
                 'ETHTUSD': 'ETH/TUSD',
                 'TUSDETH': 'TUSD/ETH',
                 'TUSDBNB': 'TUSD/BNB',
                 'ZENBTC': 'ZEN/BTC',
                 'ZENETH': 'ZEN/ETH',
                 'ZENBNB': 'ZEN/BNB',
                 'SKYBTC': 'SKY/BTC',
                 'SKYETH': 'SKY/ETH',
                 'SKYBNB': 'SKY/BNB',
                 'EOSUSDT': 'EOS/USDT',
                 'EOSBNB': 'EOS/BNB',
                 'CVCBTC': 'CVC/BTC',
                 'CVCETH': 'CVC/ETH',
                 'CVCBNB': 'CVC/BNB',
                 'THETABTC': 'THETA/BTC',
                 'THETAETH': 'THETA/ETH',
                 'THETABNB': 'THETA/BNB',
                 'XRPBNB': 'XRP/BNB',
                 'TUSDUSDT': 'TUSD/USDT',
                 'IOTAUSDT': 'IOTA/USDT',
                 'XLMUSDT': 'XLM/USDT',
                 'IOTXBTC': 'IOTX/BTC',
                 'IOTXETH': 'IOTX/ETH',
                 'QKCBTC': 'QKC/BTC',
                 'QKCETH': 'QKC/ETH',
                 'AGIBTC': 'AGI/BTC',
                 'AGIETH': 'AGI/ETH',
                 'AGIBNB': 'AGI/BNB',
                 'NXSBTC': 'NXS/BTC',
                 'NXSETH': 'NXS/ETH',
                 'NXSBNB': 'NXS/BNB',
                 'ENJBNB': 'ENJ/BNB',
                 'DATABTC': 'DATA/BTC',
                 'DATAETH': 'DATA/ETH',
                 'ONTUSDT': 'ONT/USDT',
                 'TRXBNB': 'TRX/BNB',
                 'TRXUSDT': 'TRX/USDT',
                 'ETCUSDT': 'ETC/USDT',
                 'ETCBNB': 'ETC/BNB',
                 'ICXUSDT': 'ICX/USDT',
                 'SCBTC': 'SC/BTC',
                 'SCETH': 'SC/ETH',
                 'SCBNB': 'SC/BNB',
                 'NPXSBTC': 'NPXS/BTC',
                 'NPXSETH': 'NPXS/ETH',
                 'VENUSDT': 'VEN/USDT',
                 'KEYBTC': 'KEY/BTC',
                 'KEYETH': 'KEY/ETH',
                 'NASBTC': 'NAS/BTC',
                 'NASETH': 'NAS/ETH',
                 'NASBNB': 'NAS/BNB',
                 'MFTBTC': 'MFT/BTC',
                 'MFTETH': 'MFT/ETH',
                 'MFTBNB': 'MFT/BNB',
                 'DENTBTC': 'DENT/BTC',
                 'DENTETH': 'DENT/ETH',
                 'ARDRBTC': 'ARDR/BTC',
                 'ARDRETH': 'ARDR/ETH',
                 'ARDRBNB': 'ARDR/BNB',
                 'NULSUSDT': 'NULS/USDT',
                 'HOTBTC': 'HOT/BTC',
                 'HOTETH': 'HOT/ETH',
                 'VETBTC': 'VET/BTC',
                 'VETETH': 'VET/ETH',
                 'VETUSDT': 'VET/USDT',
                 'VETBNB': 'VET/BNB',
                 'DOCKBTC': 'DOCK/BTC',
                 'DOCKETH': 'DOCK/ETH',
                 'POLYBTC': 'POLY/BTC',
                 'POLYBNB': 'POLY/BNB',
                 'PHXBTC': 'PHX/BTC',
                 'PHXETH': 'PHX/ETH',
                 'PHXBNB': 'PHX/BNB',
                 'HCBTC': 'HC/BTC',
                 'HCETH': 'HC/ETH',
                 'GOBTC': 'GO/BTC',
                 'GOBNB': 'GO/BNB',
                 'PAXBTC': 'PAX/BTC',
                 'PAXBNB': 'PAX/BNB',
                 'PAXUSDT': 'PAX/USDT',
                 'PAXETH': 'PAX/ETH',
                 'RVNBTC': 'RVN/BTC',
                 'RVNBNB': 'RVN/BNB',
                 'DCRBTC': 'DCR/BTC',
                 'DCRBNB': 'DCR/BNB',
                 'USDCBNB': 'USDC/BNB',
                 'USDCBTC': 'USDC/BTC',
                 'MITHBTC': 'MITH/BTC',
                 'MITHBNB': 'MITH/BNB',
                 'BCHABCBTC': 'BCH/BTC',
                 'BCHSVBTC': 'BSV/BTC',
                 'BCHABCUSDT': 'BCH/USDT',
                 'BCHSVUSDT': 'BSV/USDT',
                 'BNBPAX': 'BNB/PAX',
                 'BTCPAX': 'BTC/PAX',
                 'ETHPAX': 'ETH/PAX',
                 'XRPPAX': 'XRP/PAX',
                 'EOSPAX': 'EOS/PAX',
                 'XLMPAX': 'XLM/PAX',
                 'RENBTC': 'REN/BTC',
                 'RENBNB': 'REN/BNB',
                 'BNBTUSD': 'BNB/TUSD',
                 'XRPTUSD': 'XRP/TUSD',
                 'EOSTUSD': 'EOS/TUSD',
                 'XLMTUSD': 'XLM/TUSD',
                 'BNBUSDC': 'BNB/USDC',
                 'BTCUSDC': 'BTC/USDC',
                 'ETHUSDC': 'ETH/USDC',
                 'XRPUSDC': 'XRP/USDC',
                 'EOSUSDC': 'EOS/USDC',
                 'XLMUSDC': 'XLM/USDC',
                 'USDCUSDT': 'USDC/USDT',
                 'ADATUSD': 'ADA/TUSD',
                 'TRXTUSD': 'TRX/TUSD',
                 'NEOTUSD': 'NEO/TUSD',
                 'TRXXRP': 'TRX/XRP',
                 'XZCXRP': 'XZC/XRP',
                 'PAXTUSD': 'PAX/TUSD',
                 'USDCTUSD': 'USDC/TUSD',
                 'USDCPAX': 'USDC/PAX',
                 'LINKUSDT': 'LINK/USDT',
                 'LINKTUSD': 'LINK/TUSD',
                 'LINKPAX': 'LINK/PAX',
                 'LINKUSDC': 'LINK/USDC',
                 'WAVESUSDT': 'WAVES/USDT',
                 'WAVESTUSD': 'WAVES/TUSD',
                 'WAVESPAX': 'WAVES/PAX',
                 'WAVESUSDC': 'WAVES/USDC',
                 'BCHABCTUSD': 'BCH/TUSD',
                 'BCHABCPAX': 'BCH/PAX',
                 'BCHABCUSDC': 'BCH/USDC',
                 'BCHSVTUSD': 'BSV/TUSD',
                 'BCHSVPAX': 'BSV/PAX',
                 'BCHSVUSDC': 'BSV/USDC',
                 'LTCTUSD': 'LTC/TUSD',
                 'LTCPAX': 'LTC/PAX',
                 'LTCUSDC': 'LTC/USDC',
                 'TRXPAX': 'TRX/PAX',
                 'TRXUSDC': 'TRX/USDC',
                 'BTTBTC': 'BTT/BTC',
                 'BTTBNB': 'BTT/BNB',
                 'BTTUSDT': 'BTT/USDT',
                 'BNBUSDS': 'BNB/USDS',
                 'BTCUSDS': 'BTC/USDS',
                 'USDSUSDT': 'USDS/USDT',
                 'USDSPAX': 'USDS/PAX',
                 'USDSTUSD': 'USDS/TUSD',
                 'USDSUSDC': 'USDS/USDC',
                 'BTTPAX': 'BTT/PAX',
                 'BTTTUSD': 'BTT/TUSD',
                 'BTTUSDC': 'BTT/USDC',
                 'ONGBNB': 'ONG/BNB',
                 'ONGBTC': 'ONG/BTC',
                 'ONGUSDT': 'ONG/USDT',
                 'HOTBNB': 'HOT/BNB',
                 'HOTUSDT': 'HOT/USDT',
                 'ZILUSDT': 'ZIL/USDT',
                 'ZRXBNB': 'ZRX/BNB',
                 'ZRXUSDT': 'ZRX/USDT',
                 'FETBNB': 'FET/BNB',
                 'FETBTC': 'FET/BTC',
                 'FETUSDT': 'FET/USDT',
                 'BATUSDT': 'BAT/USDT',
                 'XMRBNB': 'XMR/BNB',
                 'XMRUSDT': 'XMR/USDT',
                 'ZECBNB': 'ZEC/BNB',
                 'ZECUSDT': 'ZEC/USDT',
                 'ZECPAX': 'ZEC/PAX',
                 'ZECTUSD': 'ZEC/TUSD',
                 'ZECUSDC': 'ZEC/USDC',
                 'IOSTBNB': 'IOST/BNB',
                 'IOSTUSDT': 'IOST/USDT',
                 'CELRBNB': 'CELR/BNB',
                 'CELRBTC': 'CELR/BTC',
                 'CELRUSDT': 'CELR/USDT',
                 'ADAPAX': 'ADA/PAX',
                 'ADAUSDC': 'ADA/USDC',
                 'NEOPAX': 'NEO/PAX',
                 'NEOUSDC': 'NEO/USDC',
                 'DASHBNB': 'DASH/BNB',
                 'DASHUSDT': 'DASH/USDT',
                 'NANOUSDT': 'NANO/USDT',
                 'OMGBNB': 'OMG/BNB',
                 'OMGUSDT': 'OMG/USDT',
                 'THETAUSDT': 'THETA/USDT',
                 'ENJUSDT': 'ENJ/USDT',
                 'MITHUSDT': 'MITH/USDT',
                 'MATICBNB': 'MATIC/BNB',
                 'MATICBTC': 'MATIC/BTC',
                 'MATICUSDT': 'MATIC/USDT',
                 'ATOMBNB': 'ATOM/BNB',
                 'ATOMBTC': 'ATOM/BTC',
                 'ATOMUSDT': 'ATOM/USDT',
                 'ATOMUSDC': 'ATOM/USDC',
                 'ATOMPAX': 'ATOM/PAX',
                 'ATOMTUSD': 'ATOM/TUSD',
                 'ETCUSDC': 'ETC/USDC',
                 'ETCPAX': 'ETC/PAX',
                 'ETCTUSD': 'ETC/TUSD',
                 'BATUSDC': 'BAT/USDC',
                 'BATPAX': 'BAT/PAX',
                 'BATTUSD': 'BAT/TUSD',
                 'PHBBNB': 'PHB/BNB',
                 'PHBBTC': 'PHB/BTC',
                 'PHBUSDC': 'PHB/USDC',
                 'PHBTUSD': 'PHB/TUSD',
                 'PHBPAX': 'PHB/PAX',
                 'TFUELBNB': 'TFUEL/BNB',
                 'TFUELBTC': 'TFUEL/BTC',
                 'TFUELUSDT': 'TFUEL/USDT',
                 'TFUELUSDC': 'TFUEL/USDC',
                 'TFUELTUSD': 'TFUEL/TUSD',
                 'TFUELPAX': 'TFUEL/PAX',
                 'ONEBNB': 'ONE/BNB',
                 'ONEBTC': 'ONE/BTC',
                 'ONEUSDT': 'ONE/USDT',
                 'ONETUSD': 'ONE/TUSD',
                 'ONEPAX': 'ONE/PAX',
                 'ONEUSDC': 'ONE/USDC',
                 'FTMBNB': 'FTM/BNB',
                 'FTMBTC': 'FTM/BTC',
                 'FTMUSDT': 'FTM/USDT',
                 'FTMTUSD': 'FTM/TUSD',
                 'FTMPAX': 'FTM/PAX',
                 'FTMUSDC': 'FTM/USDC',
                 'BTCBBTC': 'BTCB/BTC',
                 'BCPTTUSD': 'BCPT/TUSD',
                 'BCPTPAX': 'BCPT/PAX',
                 'BCPTUSDC': 'BCPT/USDC',
                 'ALGOBNB': 'ALGO/BNB',
                 'ALGOBTC': 'ALGO/BTC',
                 'ALGOUSDT': 'ALGO/USDT',
                 'ALGOTUSD': 'ALGO/TUSD',
                 'ALGOPAX': 'ALGO/PAX',
                 'ALGOUSDC': 'ALGO/USDC',
                 'USDSBUSDT': 'USDSB/USDT',
                 'USDSBUSDS': 'USDSB/USDS',
                 'GTOUSDT': 'GTO/USDT',
                 'GTOPAX': 'GTO/PAX',
                 'GTOTUSD': 'GTO/TUSD',
                 'GTOUSDC': 'GTO/USDC',
                 'ERDBNB': 'ERD/BNB',
                 'ERDBTC': 'ERD/BTC',
                 'ERDUSDT': 'ERD/USDT',
                 'ERDPAX': 'ERD/PAX',
                 'ERDUSDC': 'ERD/USDC',
                 'DOGEBNB': 'DOGE/BNB',
                 'DOGEBTC': 'DOGE/BTC',
                 'DOGEUSDT': 'DOGE/USDT',
                 'DOGEPAX': 'DOGE/PAX',
                 'DOGEUSDC': 'DOGE/USDC',
                 'DUSKBNB': 'DUSK/BNB',
                 'DUSKBTC': 'DUSK/BTC',
                 'DUSKUSDT': 'DUSK/USDT',
                 'DUSKUSDC': 'DUSK/USDC',
                 'DUSKPAX': 'DUSK/PAX',
                 'BGBPUSDC': 'BGBP/USDC',
                 'ANKRBNB': 'ANKR/BNB',
                 'ANKRBTC': 'ANKR/BTC',
                 'ANKRUSDT': 'ANKR/USDT',
                 'ANKRTUSD': 'ANKR/TUSD',
                 'ANKRPAX': 'ANKR/PAX',
                 'ANKRUSDC': 'ANKR/USDC',
                 'ONTPAX': 'ONT/PAX',
                 'ONTUSDC': 'ONT/USDC',
                 'WINBNB': 'WIN/BNB',
                 'WINBTC': 'WIN/BTC',
                 'WINUSDT': 'WIN/USDT',
                 'WINUSDC': 'WIN/USDC',
                 'COSBNB': 'COS/BNB',
                 'COSBTC': 'COS/BTC',
                 'COSUSDT': 'COS/USDT'}
