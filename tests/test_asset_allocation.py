import unittest
from asset_allocation import AssetClass, AssetClassCategory, Portfolio, Holding
from asset_allocation.quote_service import FakeQuoteService

class TestHolding(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({"AAPL": 100.0})
        
    def test_creation(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)
        self.assertEqual(holding.value, 1000.0)  # 10 shares * $100 per share

class TestAssetClass(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0
        })
        self.holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.asset_class = AssetClass("US Equity", [self.holding], target_weight=0.4)

    def test_creation(self):
        self.assertEqual(self.asset_class.name, "US Equity")
        self.assertEqual(self.asset_class.value, 1000.0)
        self.assertEqual(self.asset_class.target_weight, 0.4)
        self.assertEqual(len(self.asset_class.children), 1)

    def test_actual_weight_calculation(self):
        self.assertEqual(self.asset_class.actual_weight(2000.0), 0.5)  # 1000/2000 = 0.5
        self.assertEqual(self.asset_class.actual_weight(1000.0), 1.0)  # 1000/1000 = 1.0
        self.assertEqual(self.asset_class.actual_weight(4000.0), 0.25)  # 1000/4000 = 0.25

    def test_fractional_deviation_calculation(self):
        # Overweight case: 25% overweight (0.5/0.4 - 1 = 0.25)
        self.assertEqual(self.asset_class.fractional_deviation(2000.0), 0.25)
        
        # Underweight case: 37.5% underweight (0.25/0.4 - 1 = -0.375)
        self.assertEqual(self.asset_class.fractional_deviation(4000.0), -0.375)
        
        # Perfectly balanced case: 0% deviation (0.4/0.4 - 1 = 0.0)
        self.assertEqual(self.asset_class.fractional_deviation(2500.0), 0.0)

    def test_multiple_holdings(self):
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        asset_class = AssetClass("Tech", [self.holding, holding2], target_weight=0.6)
        self.assertEqual(asset_class.value, 2000.0)  # 1000 + 1000
        self.assertEqual(asset_class.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5

    def test_invalid_target_weight(self):
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [self.holding], target_weight=-0.1)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [self.holding], target_weight=1.1)

    def test_invalid_portfolio_value(self):
        with self.assertRaises(ValueError):
            self.asset_class.actual_weight(0.0)
        with self.assertRaises(ValueError):
            self.asset_class.actual_weight(-1000.0)
        with self.assertRaises(ValueError):
            self.asset_class.fractional_deviation(0.0)
        with self.assertRaises(ValueError):
            self.asset_class.fractional_deviation(-1000.0)

class TestAssetClassCategory(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "TLT": 100.0
        })
        self.holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        self.holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        self.us_equity = AssetClass("US Equity", [self.holding1], target_weight=0.4)
        self.intl_equity = AssetClass("International Equity", [self.holding2], target_weight=0.2)
        self.equity = AssetClassCategory("Equity", [self.us_equity, self.intl_equity])

    def test_creation(self):
        self.assertEqual(self.equity.name, "Equity")
        self.assertEqual(self.equity.value, 2000.0)
        self.assertAlmostEqual(self.equity.target_weight, 0.6)  # Sum of children's weights
        self.assertEqual(len(self.equity.children), 2)

    def test_actual_weight_calculation(self):
        self.assertEqual(self.equity.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5
        self.assertEqual(self.equity.actual_weight(2000.0), 1.0)  # 2000/2000 = 1.0
        self.assertEqual(self.equity.actual_weight(8000.0), 0.25)  # 2000/8000 = 0.25

    def test_fractional_deviation_calculation(self):
        # Underweight case: 16.7% underweight (0.5/0.6 - 1 = -0.167)
        self.assertAlmostEqual(self.equity.fractional_deviation(4000.0), -0.167, places=3)
        
        # Overweight case: 66.7% overweight (1.0/0.6 - 1 = 0.667)
        self.assertAlmostEqual(self.equity.fractional_deviation(2000.0), 0.667, places=3)
        
        # Perfectly balanced case: 0% deviation (0.6/0.6 - 1 = 0.0)
        self.assertAlmostEqual(self.equity.fractional_deviation(3333.33), 0.0, places=3)

    def test_nested_categories(self):
        holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        bonds = AssetClass("Bonds", [holding3], target_weight=0.4)
        fixed_income = AssetClassCategory("Fixed Income", [bonds])
        self.assertEqual(fixed_income.value, 2000.0)  # 20 shares * $100
        self.assertEqual(fixed_income.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5

    def test_invalid_portfolio_value(self):
        with self.assertRaises(ValueError):
            self.equity.actual_weight(0.0)
        with self.assertRaises(ValueError):
            self.equity.actual_weight(-2000.0)
        with self.assertRaises(ValueError):
            self.equity.fractional_deviation(0.0)
        with self.assertRaises(ValueError):
            self.equity.fractional_deviation(-2000.0)

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "TLT": 100.0
        })
        self.holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        self.holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        self.holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        self.us_equity = AssetClass("US Equity", [self.holding1], target_weight=0.4)
        self.intl_equity = AssetClass("International Equity", [self.holding2], target_weight=0.2)
        self.bonds = AssetClass("Bonds", [self.holding3], target_weight=0.4)

    def test_empty_portfolio(self):
        portfolio = Portfolio([], cash_value=1000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, None)
        self.assertEqual(portfolio.value, 1000.0)

    def test_portfolio_with_cash_target(self):
        portfolio = Portfolio([], cash_value=1000.0, cash_target=2000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)

    def test_valid_portfolio_creation(self):
        portfolio = Portfolio([self.us_equity, self.intl_equity, self.bonds])
        self.assertEqual(portfolio.value, 4000.0)  # 1000 + 1000 + 2000

    def test_invalid_target_weights(self):
        invalid_equity = AssetClass("Invalid", [self.holding1], target_weight=0.3)
        with self.assertRaises(ValueError) as cm:
            Portfolio([invalid_equity, self.intl_equity])
        self.assertIn("Sum of target weights must be 1.0", str(cm.exception))

    def test_nested_categories(self):
        equity = AssetClassCategory("Equity", [self.us_equity, self.intl_equity])
        fixed_income = AssetClassCategory("Fixed Income", [self.bonds])
        portfolio = Portfolio([equity, fixed_income], cash_value=1000.0, cash_target=2000.0)
        
        self.assertEqual(portfolio.value, 5000.0)  # 2000 + 2000 + 1000 cash
        self.assertEqual(equity.value, 2000.0)  # AAPL + MSFT
        self.assertEqual(fixed_income.value, 2000.0)  # TLT
        self.assertEqual(len(portfolio.children), 2)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)
        self.assertAlmostEqual(equity.target_weight, 0.6)  # Sum of children's weights
        self.assertAlmostEqual(fixed_income.target_weight, 0.4)  # Sum of children's weights

if __name__ == '__main__':
    unittest.main() 