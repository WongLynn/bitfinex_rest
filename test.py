import unittest
import bitfinex


class Test(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self.public = bitfinex.Public()
        self.auth = bitfinex.Auth()

    def test_get_last_price(self):
        last_price = self.public.get_last_price('btc', 'usd')
        self.assertIsInstance(last_price, float)

    def test_ticker(self):
        ticker = self.public.get_ticker('btc', 'usd')
        self.assertIsInstance(ticker, list)
        for x in ticker:
            self.assertIsInstance(x, float)

    def test_get_orderbook(self):
        orderbook = self.public.get_orderbook('btc', 'usd')
        self.assertIsInstance(orderbook, list)
        for x in orderbook[:2]:
            self.assertIsInstance(x, float)
        for x in orderbook[2:]:
            self.assertIsInstance(x, list)
            for i in x:
                self.assertIsInstance(i, float)

    def test_get_candle(self):
        candle = self.public.get_1m_candle('btc', 'usd')
        self.assertIsInstance(candle, list)
        for x in candle:
            self.assertIsInstance(x, float)

    def test_get_balance(self):
        balance = self.auth.get_balance()
        self.assertIsInstance(balance, dict)
        for x in balance.values():
            self.assertIsInstance(x, float)

    def test_get_active_orders(self):
        active = self.auth.get_active_orders()
        self.assertIsInstance(active, list)

    def test_get_trade_history(self):
        history = self.auth.get_history_trades('btc', 'usd')
        self.assertIsInstance(history, dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)
