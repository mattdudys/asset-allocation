import unittest
from asset_allocation import AssetClass, AssetClassCategory, Portfolio, Holding
from asset_allocation.quote_service import FakeQuoteService

class TestHolding(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({"AAPL": 100.0})
        
    def test_holding_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)

    def test_holding_value_calculation(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.assertEqual(holding.value, 1000.0)  # 10 shares * $100 per share

class TestAssetClass(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0
        })

    def test_asset_class_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        
        self.assertEqual(asset_class.name, "US Equity")
        self.assertEqual(asset_class.target_weight, 0.4)
        self.assertEqual(len(asset_class.children), 1)

    def test_asset_class_value_sums_holdings(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        self.assertEqual(asset_class.value, 1000.0)  # 10 shares * $100

    def test_asset_class_actual_weight_when_overweight(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # Value is 1000, portfolio is 2000, so weight is 0.5 (25% overweight)
        self.assertEqual(asset_class.actual_weight(2000.0), 0.5)

    def test_asset_class_actual_weight_when_underweight(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # Value is 1000, portfolio is 4000, so weight is 0.25 (37.5% underweight)
        self.assertEqual(asset_class.actual_weight(4000.0), 0.25)

    def test_asset_class_actual_weight_when_balanced(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # Value is 1000, portfolio is 2500, so weight is 0.4 (perfectly balanced)
        self.assertEqual(asset_class.actual_weight(2500.0), 0.4)

    def test_asset_class_fractional_deviation_when_overweight(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # (0.5/0.4) - 1 = 0.25 (25% overweight)
        self.assertEqual(asset_class.fractional_deviation(2000.0), 0.25)

    def test_asset_class_fractional_deviation_when_underweight(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # (0.25/0.4) - 1 = -0.375 (37.5% underweight)
        self.assertEqual(asset_class.fractional_deviation(4000.0), -0.375)

    def test_asset_class_fractional_deviation_when_balanced(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        # (0.4/0.4) - 1 = 0.0 (perfectly balanced)
        self.assertEqual(asset_class.fractional_deviation(2500.0), 0.0)

    def test_asset_class_rejects_negative_target_weight(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_weight=-0.1)

    def test_asset_class_rejects_target_weight_over_one(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_weight=1.1)

    def test_asset_class_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        with self.assertRaises(ValueError):
            asset_class.actual_weight(0.0)

    def test_asset_class_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        with self.assertRaises(ValueError):
            asset_class.actual_weight(-1000.0)

    def test_asset_class_with_multiple_holdings(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        asset_class = AssetClass("Tech", [holding1, holding2], target_weight=0.6)
        
        self.assertEqual(asset_class.value, 2000.0)  # 1000 + 1000
        self.assertEqual(asset_class.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5

class TestAssetClassCategory(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "TLT": 100.0
        })

    def test_category_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        category = AssetClassCategory("Equity", [asset_class])
        
        self.assertEqual(category.name, "Equity")
        self.assertEqual(len(category.children), 1)

    def test_category_value_sums_children(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        self.assertEqual(category.value, 2000.0)  # 1000 + 1000
        self.assertAlmostEqual(category.target_weight, 0.6)  # 0.4 + 0.2

    def test_category_actual_weight_when_underweight(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # Value is 2000, portfolio is 4000, so weight is 0.5 (16.7% underweight)
        self.assertEqual(category.actual_weight(4000.0), 0.5)

    def test_category_actual_weight_when_overweight(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # Value is 2000, portfolio is 2000, so weight is 1.0 (66.7% overweight)
        self.assertEqual(category.actual_weight(2000.0), 1.0)

    def test_category_actual_weight_when_balanced(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        self.assertEqual(category.actual_weight(2000 / 0.6), 0.6)

    def test_category_fractional_deviation_when_underweight(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (0.5/0.6) - 1 = -0.167 (16.7% underweight)
        self.assertAlmostEqual(category.fractional_deviation(4000.0), -0.167, places=3)

    def test_category_fractional_deviation_when_overweight(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (1.0/0.6) - 1 = 0.667 (66.7% overweight)
        self.assertAlmostEqual(category.fractional_deviation(2000.0), 0.667, places=3)

    def test_category_fractional_deviation_when_balanced(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (0.6/0.6) - 1 = 0.0 (perfectly balanced)
        self.assertAlmostEqual(category.fractional_deviation(3333.33), 0.0, places=3)

    def test_category_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        category = AssetClassCategory("Equity", [asset_class])
        with self.assertRaises(ValueError):
            category.actual_weight(0.0)

    def test_category_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        category = AssetClassCategory("Equity", [asset_class])
        with self.assertRaises(ValueError):
            category.actual_weight(-2000.0)

    def test_nested_categories(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        bonds = AssetClass("Bonds", [holding3], target_weight=0.4)
        
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        fixed_income = AssetClassCategory("Fixed Income", [bonds])
        
        self.assertEqual(equity.value, 2000.0)  # AAPL + MSFT
        self.assertEqual(fixed_income.value, 2000.0)  # TLT
        self.assertAlmostEqual(equity.target_weight, 0.6)  # 0.4 + 0.2
        self.assertAlmostEqual(fixed_income.target_weight, 0.4)

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "TLT": 100.0
        })

    def test_empty_portfolio_creation(self):
        portfolio = Portfolio([], cash_value=1000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, None)
        self.assertEqual(portfolio.value, 1000.0)

    def test_portfolio_with_cash_target(self):
        portfolio = Portfolio([], cash_value=1000.0, cash_target=2000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)

    def test_portfolio_value_sums_children_and_cash(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        bonds = AssetClass("Bonds", [holding3], target_weight=0.4)
        
        portfolio = Portfolio([us_equity, intl_equity, bonds], cash_value=1000.0)
        self.assertEqual(portfolio.value, 5000.0)  # 1000 + 1000 + 2000 + 1000 cash

    def test_portfolio_rejects_invalid_target_weights(self):
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        invalid_equity = AssetClass("Invalid", [holding], target_weight=0.3)
        intl_equity = AssetClass("International Equity", [holding], target_weight=0.4)
        
        with self.assertRaises(ValueError) as cm:
            Portfolio([invalid_equity, intl_equity])
        self.assertIn("Sum of target weights must be 1.0", str(cm.exception))

    def test_portfolio_with_nested_categories(self):
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        bonds = AssetClass("Bonds", [holding3], target_weight=0.4)
        
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        fixed_income = AssetClassCategory("Fixed Income", [bonds])
        
        portfolio = Portfolio([equity, fixed_income], cash_value=1000.0, cash_target=2000.0)
        
        self.assertEqual(portfolio.value, 5000.0)  # 2000 + 2000 + 1000 cash
        self.assertEqual(equity.value, 2000.0)  # AAPL + MSFT
        self.assertEqual(fixed_income.value, 2000.0)  # TLT
        self.assertEqual(len(portfolio.children), 2)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)
        self.assertAlmostEqual(equity.target_weight, 0.6)  # 0.4 + 0.2
        self.assertAlmostEqual(fixed_income.target_weight, 0.4)

if __name__ == '__main__':
    unittest.main() 