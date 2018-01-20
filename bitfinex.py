import hmac
import json
import time
import yaml
import base64
import hashlib
import requests


URI = 'https://api.bitfinex.com'

with open('settings.yaml') as f:
    cfg = yaml.load(f)


class Public:
    def _public_call(self, urlpath, params=None):
        if params is None:
            params = {}
        url = URI + '/v1/' + urlpath
        response = requests.get(url, params=params, timeout=5)
        if response.status_code not in (200, 201, 202):
            response.raise_for_status()
        return response.json()

    def _ticker(self, pair_main, pair_second):
        symbol = pair_main + pair_second
        return self._public_call('pubticker/{}'.format(symbol))

    def _orderbook(self, pair_main, pair_second, limit=50):
        symbol = pair_main + pair_second
        return self._public_call('book/{}'.format(symbol), {'limit_bids': limit, 'limit_asks': limit})

    def _trades(self, pair_main, pair_second, limit=50):
        symbol = pair_main + pair_second
        return self._public_call('trades/{}'.format(symbol), {'limit_trades': limit})

    def get_last_price(self, pair_main=cfg['pair_main'], pair_second=cfg['pair_second']):
        """Return value of last exchange trade"""
        trades = self._trades(pair_main, pair_second, limit=20)
        last_trade = [float(value['price']) for value in trades][0]
        return last_trade

    def get_ticker(self, pair_main=cfg['pair_main'], pair_second=cfg['pair_second']):
        """"Return array with ticker info, 0: high, 1: low, 2: last trade, 3: 24h volume"""
        ticker = self._ticker(pair_main, pair_second)
        return [float(ticker['high']), float(ticker['low']), float(ticker['last_price']), float(ticker['volume'])]

    def get_orderbook(self, pair_main=cfg['pair_main'], pair_second=cfg['pair_second']):
        """Return array with orderbook: best ask, best bid and splitted book asks/bids
           0: best_ask, 1: best_bid, 2: asks, 3: bids"""
        orders = self._orderbook(pair_main, pair_second, limit=100)
        asks = [float(value['price']) for value in orders['asks']]
        bids = [float(value['price']) for value in orders['bids']]
        order_book = [asks[0], bids[0], asks, bids]
        return order_book

    def get_1m_candle(self, pair_main=cfg['pair_main'], pair_second=cfg['pair_second'], interval=1):
        """Making 1 minute candle from the moment of the call
           0: open, 1:close, 2: min, 3: max, 4: volume, 5: volume_buy, 6: volume_sell, 7: timestamp"""
        start = time.time()
        trades = self._trades(pair_main, pair_second, limit=200)
        timestamp = start - time.time()
        trade_list = [float(value['price']) for value in trades
                      if timestamp - interval * 60 <= int(value['timestamp'])]
        if trade_list:
            volume = sum([float(value['amount']) for value in trades
                          if timestamp - interval * 60 <= int(value['timestamp'])])
            volume_buy = sum([float(value['amount']) for value in trades
                              if timestamp - interval * 60 <= int(value['timestamp']) and value['type'] == 'buy'])
            volume_sell = sum([float(value['amount']) for value in trades
                               if timestamp - interval * 60 <= int(value['timestamp']) and value['type'] == 'sell'])
            candle = [trade_list[-1], trade_list[0], min(trade_list), max(trade_list),
                      volume, volume_buy, volume_sell, time.time()]
            return candle


class Auth:
    def __init__(self, public_key=None, secret_key=None):
        if public_key and secret_key:
            self.public_key = public_key
            self.secret_key = secret_key
        else:
            self.public_key = cfg['public_key']
            self.secret_key = cfg['secret_key']

    def _nonce(self):
        nonce = round(time.time() * 1000)
        return str(nonce)

    def _sign(self, params):
        payload_json = json.dumps(params)
        payload = base64.b64encode(payload_json.encode('utf-8'))
        h = hmac.new(self.secret_key.encode('utf-8'), payload, hashlib.sha384)
        signature = h.hexdigest()
        headers = {
            'X-BFX-APIKEY': self.public_key,
            'X-BFX-PAYLOAD': payload,
            'X-BFX-SIGNATURE': signature
        }
        return headers

    def _auth_call(self, params):
        url = URI + params['request']
        params['nonce'] = self._nonce()
        response = requests.post(url, headers=self._sign(params), timeout=5)
        if response.status_code not in (200, 201, 202):
            print('HTTP ERR: {}, MESSAGE: {}'.format(response.status_code, response.json()))
            response.raise_for_status()
        return response.json()

    def _balance(self):
        params = {'request': '/v1/balances'}
        return self._auth_call(params)

    def _new_order(self, amount, price, side, order_type, pair_main, pair_second):
        symbol = pair_main + pair_second
        params = {'request': '/v1/order/new',
                  'symbol': symbol,
                  'amount': str(amount),
                  'price': str(price),
                  'side': side,
                  'type': order_type}
        return self._auth_call(params)

    def _cancel_order(self, order_id):
        params = {'request': '/v1/order/cancel', 'order_id': int(order_id)}
        return self._auth_call(params)

    def _order_status(self, order_id):
        params = {'request': '/v1/order/status', 'order_id': int(order_id)}
        return self._auth_call(params)

    def _active_orders(self):
        params = {'request': '/v1/orders'}
        return self._auth_call(params)

    def _history_trades(self, pair_main, pair_second):
        symbol = pair_main + pair_second
        params = {'request': '/v1/mytrades', 'symbol': symbol}
        return self._auth_call(params)

    def get_balance(self):
        """Return array with balance wallet info"""
        balance = {x['currency']: float(x['amount']) for x in self._balance()}
        return balance

    def _split_order_info(self, order):
        """Split order info 0: id, 1: side, 2: price, 3: amount, 4: timestamp"""
        order_info = [int(order['id']), order['side'], float(order['price']),
                      float(order['original_amount']), float(order['timestamp'])]
        return order_info

    def post_order(self, amount, price, side, pair_main=cfg['pair_main'],
                   pair_second=cfg['pair_second'], order_type='exchange limit'):
        """Just place order, side is buy or sell"""
        order = self._new_order(amount, price, side, pair_main, pair_second, order_type)
        return self._split_order_info(order)

    def post_cancel_order(self, order_id):
        """Cancel order, return True if order canceled"""
        cancel = self._cancel_order(order_id)
        status = self._order_status(cancel['id'])
        return True if status['is_cancelled'] else False

    def get_active_orders(self):
        """Return array with active orders(each order in list [id, symbol, price, amount, timestamp])"""
        orders = [[x['id'], x['symbol'], float(x['price']), float(x['original_amount']),
                   float(x['timestamp'])] for x in self._active_orders()]
        return orders

    def get_order_status(self, order_id):
        """Return array with order status 0: id, 1: side, 2: price, 3: amount, 4: timestamp"""
        status = self._order_status(order_id)
        return self._split_order_info(status)

    def get_history_trades(self, pair_main=cfg['pair_main'], pair_second=cfg['pair_second']):
        """Return dictionary with key order_id and value array with info
            0: type(buy or sell), 1: symbol, 2: price, 3: amount, 4: timestamp"""
        history = self._history_trades(pair_main, pair_second)
        trades = {x['order_id']: [pair_main + pair_second, x['type'].lower(),
                                  float(x['price']), float(x['amount']), float(x['timestamp'])] for x in history}
        return trades
