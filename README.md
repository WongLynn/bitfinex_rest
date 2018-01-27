# Python 3 Bitfinex Rest API Wrapper

##Quickstart:

  1. ```git clone https://github.com/enalco/bitfinex_rest.git``` or [download](https://github.com/enalco/bitfinex_rest/archive/master.zip)
  2. Install python requirements for bitfinex api via pip. ```pip3 install -r requirements.txt```
  3. Fill ```settings.yaml``` with pairs and bitfinex api keys
  4. Just **trade** =)
    
## Usage notes: 
    
  1. API splitted by public and auth. For default pairs get from ```settings.yaml```, But you can specify them explicitly.
  2. Auth API require **public and secret keys** in ```settings.yaml``` or you can specify them explicitly.
  3. By default new orders placed with type 'exchange limit', for use 'exchange market' call post order with
    argument ```order_type='exchange market'```

## Public API:

  - **Call:** ```get_last_price(pair_main, pair_second)``` or ```get_last_price()``` with config values
    - **Description:** Return last trade
    - **Output:** ```float()```
    
  - **Call:** ```get_ticker(pair_main, pair_second)``` or ```get_ticker()``` with config values
    - **Description:** Return array with ticker info, 0: high, 1: low, 2: last trade, 3: 24h volume
    - **Output:** ```[float, float, float, float]```
    
  - **Call:** ```get_orderbook(pair_main, pair_second)``` or ```get_orderbook()``` with config values
    - **Description:** Return array with orderbook, 0: best ask, 1: best bid, 2: asks, 3: bids
    - **Output:** ```[float, float, [float], [float]]```
    
  - **Call:** ```get_1m_candle(pair_main, pair_second)``` or ```get_1m_candle()``` with config values
    - **Description:** Return array with 1 minute values from the moment of the call
      0: open, 1: close, 2: min, 3: max, 4: volume, 5: volume buy, 6: volume sell, 7 timestamp
    - **Output:** ```[float, float, float, float, float, float, float, float]```


## Auth API:

  - **Call:** ```get_balance()```
    - **Description:** Return dictionary with balance info, pair_main: pair_second, for ex btc: 0.1
    - **Output:** ```{str: float}```
    
  - **Call:** ```post_order(amount, price, side, pair_main, pair_second)``` or ```post_order(amount, price, side)``` with config values
    - **Description:** Return array with order info, side is buy or sell, 0: id, 1: side, 2: price, 3: amount, 4: timestamp
    - **Output:** ```[str, str, float, float, float]```
    
  - **Call:** ```post_cancel_order(order_id)```
    - **Description:** Cancel order by id, return True if cancel success
    - **Output:** ```True``` or ```False```
    
  - **Call:** ```get_active_orders()```
    - **Description:** Return array with active orders(each order in list), 
      0: id, 1: symbol, 2: price, 3: amount, 4: timestamp
    - **Output:** ```[[str, str, str, float, float, float], ...]]```

  - **Call:** ```get_trade_history(pair_main, pair_second)``` or ```trade_history()``` with config values
    - **Description:** Return dictionary with key order_id and value array with info
      0: type(buy or sell), 1: symbol, 2: price, 3: amount, 4: timestamp
    - **Output:** ```{'str': [str, str, float, float, float], ...}```


## TO DO:

  * Manage exceptions
  * Add more tests
  * ...