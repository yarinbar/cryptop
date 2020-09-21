
# Cryptop - A framework to manage positions using algorithmic trading

This library is a work in progress, and it is **not** finished yet.

Cryptop is a framework that interacts with `Binance` using a strategy you come up with and runs it. Cryptop will post orders, calculate returns and sync with your trading account all according to your strategy.

### Prerequisites

In order to use this library you'll need the following prerequisites:

```
numpy
ccxt
binance api
matplotlib
sklearn 
pandas
ta-lib
```


### Components

**dataset.py**

1. Dataset - a class that contains the candle information from `since` date until the limit (depends on the api of `binance` as well). This class will also take care of the TA for you as it happens automatically when created. Use the `plot` method to plot the dataset into an OHLCV graph.

2. Data - The `Data` class is broader and manages updates to existing datasets and saves it to a convenient `csv` file in the "data directory.


**settings.py**

There you will find all kinds of settings that changes the behavior of your bot.


**position.py**

1. Position - a class that manages an existing position. A position is created inactive and has to be opened in order to be activated. Since a position can be partially filled, canceled or closed in a blink of an eye, the method update position handles those scenarios. A stop-loss can be placed as well as maximal time the order can stay open. 


**startegy.py - not done**

1. Strategy - has a name a signaling method and a signal handler. The signal of the strategy is produces based on the dataset that is passed to the method. The signal handler can use the signal handler to determine what to do with the signal (for example the signal can be `buy` where as there is no money available to the bot to spend, in this case the handler can ignore the signal).


**bot.py - not done**

1. Bot - one bot can handle one pair & interval only. It gets a list of strategies and a method `startegy_handler` which can decide which startegy to employ (ie - for quiet days mean reversion and for volatile days golden cross strategy). Each bot has 4 lists of positions:


    1. waiting to be opened - orders that are waiting to be filled
    2. open positions - partially or fully filled positions
    3. waiting to be closed - after buying, closing means selling it back to the base currency. These orders are either partially filled or not filled at all.
    4. closed - only fully filled selling positions are closed positions

Using the `update_positions` method, the bot traverses through all lists (except the closed list) and updates each position from the api. If a change happened that requires a position to change lists - this is where it happens.
Using the bot's interface, you can order it to open a position or close an open position.

## Built With

* [ccxt](https://github.com/ccxt/ccxt) - for the brokerage api
* [ta](https://github.com/bukosabino/ta) - Tenchnical analysis tool


## Authors

* **Yarin Bar**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

