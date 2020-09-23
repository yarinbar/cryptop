

# Cryptop - A framework to manage positions using algorithmic trading

Cryptop is a framework that interacts with `Binance` using a custom strategy and runs it. Cryptop will post orders, calculate returns and sync with your trading account all according to your strategy. You may also set a spending limit which will make the bot avoid overspending your money.

### Prerequisites

In order to use this library please make sure you habe the following libraries:

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

**book.py**

PositionBook - contains a **single** pair of coins and a 4 lists of positions:
    1. waiting to be opened - orders that are waiting to be filled
    2. open positions - partially or fully filled positions
    3. closed - after buying, closing means selling it back to the base currency. Only fully filled selling positions are closed positions
    4. canceled 

The bot checks the status of a position by fetching it using the unique `position_id` which you get after opening a position. To prevent the position book from being not up to date, there is a `sync` method that checks each position and updates the status if needed. All of the opening and closing of positions is done only through the book. It is also possible to close positions in bulk by a condition (ie all positions that are older than 24 hours, or all position which has value under 400$).


**bot.py**

Bot - Each bot has a name, stategy, pair (only one), allowance (to prevent overspending), a position book and data to work with. A bot operates soley by the strategy it is being given. This strategy tells it when to buy and sell. (Not done yet)


**config.py**

This file contains various settings that changes the way the bot behaves and trades. For example `POSITION_LIMIT = 100` prevents the bot to open more than 100 position at any given time. `MODE = TEST` ensures the bot doesnt actually posts the orders online but just simulates it localy, to run it use `MODE = RUN`.


**data.py**

Data - a class that contains the candle information. This class will also take care of the TA for you as it happens automatically when created. Use the `plot` method to plot the dataset into an OHLCV graph. This class also manages existing datas and can update and save it to a convenient `csv` file in the "data" directory.


**dataset.py**

A file that has utility functions to help create a dataset from the csv which contains a lot of information. The data set is meant to be used to train neural networks.


**manager.py**

PositionManager - a class that takes into consideration the current available spending money and can tell if the bot should or shouldnt open a position (not done yet).


**position.py**

Position - a class that manages an existing position. A position is created inactive and has to be opened in order to be activated. Since a position can be partially filled, canceled or closed in a blink of an eye, the method `update position` handles those scenarios and ensures the bot is aware of the true status of each position. A stop-loss can be placed as well as maximal time the order can stay open. This is a broader class and the following classes inherit from it. Using the `update_positions` method, the bot traverses through all lists (except the closed list) and updates each position from the api. If a change happened that requires a position to change lists - this is where it 

Long - a position where the price of an asset is supposed to go up thus you open it by buying the asset and selling later (hopefully at a higher price).

Short - a position where the price of an asset is supposed to go down thus you open it by selling the asset and buying later (hopefully at a lower price).


**startegy.py**

Strategy - has a name a signaling method and a signal handler. The signal of the strategy is produces based on the dataset that is passed to the method. The signal handler can use the signal handler to determine what to do with the signal (for example the signal can be `buy` where as there is no money available to the bot to spend, in this case the handler can ignore the signal). It's important to mention that a strategy can use a neural network model to generate signals. 


## Testing

I have created a testing folder with 3 unittests for:

1. Book
2. Position
3. Strategy

More to come in the future.


This library is a work in progress, and it is **not** finished yet.


## Built With

* [ccxt](https://github.com/ccxt/ccxt) - for the brokerage api
* [ta](https://github.com/bukosabino/ta) - Tenchnical analysis tool


## Authors

* **Yarin Bar - Technion, Israel Institute of Technology**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

