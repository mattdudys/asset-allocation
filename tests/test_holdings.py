import unittest
from asset_allocation.holding import Holding
from asset_allocation.quote_service import FakeQuoteService

class TestHolding(unittest.TestCase):
    def test_holding_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, price=100.0)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)
        self.assertEqual(holding.price, 100.0)

    def test_holding_value_calculation(self):
        holding = Holding("AAPL", 10, price=100.0)
        self.assertEqual(holding.value, 1000.0)  # 10 shares * $100 per share

    def test_holding_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            Holding("AAPL", 10, price=-100.0)

    def test_holding_rejects_zero_price(self):
        with self.assertRaises(ValueError):
            Holding("AAPL", 10, price=0.0)

    def test_holding_from_quote_service(self):
        quote_service = FakeQuoteService({"AAPL": 100.0})
        holding = Holding.from_quote_service("AAPL", 10, quote_service)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)
        self.assertEqual(holding.price, 100.0)
        self.assertEqual(holding.value, 1000.0)

    def test_holding_buy_with_sufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        spent = holding.buy(150.0)
        self.assertEqual(spent, 100.0)
        self.assertEqual(holding.shares, 11)

    def test_holding_buy_with_insufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        spent = holding.buy(50.0)
        self.assertEqual(spent, 0.0)
        self.assertEqual(holding.shares, 10)

    def test_holding_sell_full_share(self):
        holding = Holding("AAPL", 10, price=100.0)
        proceeds = holding.sell()
        self.assertEqual(proceeds, 100.0)  # 1 share * $100
        self.assertEqual(holding.shares, 9)

    def test_holding_sell_fractional_share(self):
        holding = Holding("AAPL", 0.5, price=100.0)
        proceeds = holding.sell()
        self.assertEqual(proceeds, 50.0)  # 0.5 shares * $100
        self.assertEqual(holding.shares, 0)

    def test_holding_sell_zero_shares(self):
        holding = Holding("AAPL", 0, price=100.0)
        proceeds = holding.sell()
        self.assertEqual(proceeds, 0.0)
        self.assertEqual(holding.shares, 0)

    def test_holding_sell_multiple_times(self):
        holding = Holding("AAPL", 2.5, price=100.0)
        proceeds1 = holding.sell()
        self.assertEqual(proceeds1, 100.0)  # 1 share * $100
        self.assertEqual(holding.shares, 1.5)
        
        proceeds2 = holding.sell()
        self.assertEqual(proceeds2, 100.0)  # 1 share * $100
        self.assertEqual(holding.shares, 0.5)
        
        proceeds3 = holding.sell()
        self.assertEqual(proceeds3, 50.0)  # 0.5 shares * $100
        self.assertEqual(holding.shares, 0) 