import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import AssetClass, AssetClassCategory

class TestAssetClass(unittest.TestCase):
    def test_asset_class_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        
        self.assertEqual(asset_class.name, "US Equity")
        self.assertEqual(asset_class.target_weight, 0.4)
        self.assertEqual(len(asset_class.holdings), 1)

    def test_asset_class_value_sums_holdings(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        self.assertEqual(asset_class.value, 1000.0)  # 10 shares * $100

    def test_asset_class_actual_weight_when_overweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # Value is 1000, portfolio is 2000, so weight is 0.5 (25% overweight)
        self.assertEqual(asset_class.actual_weight(2000.0), 0.5)

    def test_asset_class_actual_weight_when_underweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # Value is 1000, portfolio is 4000, so weight is 0.25 (37.5% underweight)
        self.assertEqual(asset_class.actual_weight(4000.0), 0.25)

    def test_asset_class_actual_weight_when_balanced(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # Value is 1000, portfolio is 2500, so weight is 0.4 (perfectly balanced)
        self.assertEqual(asset_class.actual_weight(2500.0), 0.4)

    def test_asset_class_fractional_deviation_when_overweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # (0.5/0.4) - 1 = 0.25 (25% overweight)
        self.assertEqual(asset_class.fractional_deviation(2000.0), 0.25)

    def test_asset_class_fractional_deviation_when_underweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # (0.25/0.4) - 1 = -0.375 (37.5% underweight)
        self.assertEqual(asset_class.fractional_deviation(4000.0), -0.375)

    def test_asset_class_fractional_deviation_when_balanced(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        # (0.4/0.4) - 1 = 0.0 (perfectly balanced)
        self.assertEqual(asset_class.fractional_deviation(2500.0), 0.0)

    def test_asset_class_rejects_negative_target_weight(self):
        holding = Holding("AAPL", 10, price=100.0)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", target_weight=-0.1, holdings=[holding])

    def test_asset_class_rejects_target_weight_over_one(self):
        holding = Holding("AAPL", 10, price=100.0)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", target_weight=1.1, holdings=[holding])

    def test_asset_class_rejects_empty_holdings(self):
        with self.assertRaises(ValueError) as cm:
            AssetClass("Invalid", target_weight=0.4, holdings=[])
        self.assertEqual(str(cm.exception), "AssetClass must have at least one holding")

    def test_asset_class_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        with self.assertRaises(ValueError):
            asset_class.actual_weight(0.0)

    def test_asset_class_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        with self.assertRaises(ValueError):
            asset_class.actual_weight(-1000.0)

    def test_asset_class_buy_with_sufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        spent = asset_class.buy(150.0, 2500.0)
        self.assertEqual(spent, 100.0)
        self.assertEqual(holding.shares, 11)

    def test_asset_class_buy_with_insufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        spent = asset_class.buy(50.0, 2500.0)
        self.assertEqual(spent, 0.0)
        self.assertEqual(holding.shares, 10)

    def test_asset_class_buy_with_multiple_holdings(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        spent = asset_class.buy(150.0, 2500.0)
        self.assertEqual(spent, 100.0)
        self.assertEqual(holding1.shares, 11)  # First holding should be bought
        self.assertEqual(holding2.shares, 10)  # Second holding should be unchanged

    def test_asset_class_sell_from_last_holding(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        proceeds = asset_class.sell()
        self.assertEqual(proceeds, 100.0)  # One share of MSFT at $100
        self.assertEqual(holding1.shares, 10)  # First holding unchanged
        self.assertEqual(holding2.shares, 9)   # Second holding reduced by 1

    def test_asset_class_sell_from_last_holding_fractional(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 0.5, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        proceeds = asset_class.sell()
        self.assertEqual(proceeds, 50.0)  # 0.5 shares of MSFT at $100
        self.assertEqual(holding1.shares, 10)  # First holding unchanged
        self.assertEqual(holding2.shares, 0)   # Second holding reduced to 0

    def test_asset_class_sell_from_second_last_when_last_empty(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        proceeds = asset_class.sell()
        self.assertEqual(proceeds, 100.0)  # One share of AAPL at $100
        self.assertEqual(holding1.shares, 9)  # First holding reduced by 1
        self.assertEqual(holding2.shares, 0)  # Second holding unchanged

    def test_asset_class_sell_returns_zero_when_all_empty(self):
        holding1 = Holding("AAPL", 0, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        proceeds = asset_class.sell()
        self.assertEqual(proceeds, 0.0)  # No shares to sell
        self.assertEqual(holding1.shares, 0)  # First holding unchanged
        self.assertEqual(holding2.shares, 0)  # Second holding unchanged

    def test_asset_class_with_multiple_holdings(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = AssetClass("Tech", target_weight=0.6, holdings=[holding1, holding2])
        
        self.assertEqual(asset_class.value, 2000.0)  # 1000 + 1000
        self.assertEqual(asset_class.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5

class TestAssetClassCategory(unittest.TestCase):
    def test_category_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        category = AssetClassCategory("Equity", [asset_class])
        
        self.assertEqual(category.name, "Equity")
        self.assertEqual(len(category.children), 1)

    def test_category_rejects_empty_children(self):
        with self.assertRaises(ValueError) as cm:
            AssetClassCategory("Invalid", [])
        self.assertEqual(str(cm.exception), "AssetClassCategory must have at least one child")

    def test_category_value_sums_children(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        self.assertEqual(category.value, 2000.0)  # 1000 + 1000
        self.assertAlmostEqual(category.target_weight, 0.6)  # 0.4 + 0.2

    def test_category_actual_weight_when_underweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # Value is 2000, portfolio is 4000, so weight is 0.5 (16.7% underweight)
        self.assertEqual(category.actual_weight(4000.0), 0.5)

    def test_category_actual_weight_when_overweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # Value is 2000, portfolio is 3000, so weight is 0.667 (11.1% overweight)
        self.assertAlmostEqual(category.actual_weight(3000.0), 0.667, places=3)

    def test_category_actual_weight_when_balanced(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # Value is 2000, portfolio is 3333.33, so weight is 0.6 (perfectly balanced)
        self.assertAlmostEqual(category.actual_weight(3333.33), 0.6, places=2)

    def test_category_fractional_deviation_when_underweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (0.5/0.6) - 1 = -0.167 (16.7% underweight)
        self.assertAlmostEqual(category.fractional_deviation(4000.0), -0.167, places=3)

    def test_category_fractional_deviation_when_overweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (0.667/0.6) - 1 = 0.111 (11.1% overweight)
        self.assertAlmostEqual(category.fractional_deviation(3000.0), 0.111, places=3)

    def test_category_fractional_deviation_when_balanced(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # (0.6/0.6) - 1 = 0.0 (perfectly balanced)
        self.assertAlmostEqual(category.fractional_deviation(3333.33), 0.0, places=2)

    def test_category_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        category = AssetClassCategory("Equity", [asset_class])
        with self.assertRaises(ValueError):
            category.actual_weight(0.0)

    def test_category_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        category = AssetClassCategory("Equity", [asset_class])
        with self.assertRaises(ValueError):
            category.actual_weight(-1000.0)

    def test_nested_categories(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        holding3 = Holding("AGG", 10, price=100.0)
        fixed_income = AssetClass("Fixed Income", target_weight=0.4, holdings=[holding3])
        
        portfolio = AssetClassCategory("Total", [equity, fixed_income])
        
        self.assertEqual(portfolio.value, 3000.0)  # 1000 + 1000 + 1000
        self.assertEqual(portfolio.target_weight, 1.0)  # 0.6 + 0.4

    def test_category_sell_from_most_overweight(self):
        # Create holdings with different weights
        holding1 = Holding("AAPL", 10, price=100.0)  # 1000
        holding2 = Holding("MSFT", 10, price=100.0)  # 1000
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # US Equity is overweight (0.4/0.4 = 1.0), Intl Equity is overweight (0.4/0.2 = 2.0)
        proceeds = category.sell(2000.0)
        self.assertEqual(proceeds, 100.0)  # Should sell from MSFT (most overweight)
        self.assertEqual(holding1.shares, 10)  # AAPL unchanged
        self.assertEqual(holding2.shares, 9)   # MSFT reduced by 1

    def test_category_sell_from_second_most_overweight(self):
        # Create holdings with different weights
        holding1 = Holding("AAPL", 10, price=100.0)  # 1000
        holding2 = Holding("MSFT", 0, price=100.0)   # 0
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        # US Equity is overweight (0.4/0.4 = 1.0), Intl Equity is empty
        proceeds = category.sell(1000.0)
        self.assertEqual(proceeds, 100.0)  # Should sell from AAPL (second most overweight)
        self.assertEqual(holding1.shares, 9)  # AAPL reduced by 1
        self.assertEqual(holding2.shares, 0)  # MSFT unchanged

    def test_category_sell_returns_zero_when_all_empty(self):
        holding1 = Holding("AAPL", 0, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        category = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        proceeds = category.sell(1000.0)  # Using a positive portfolio value
        self.assertEqual(proceeds, 0.0)  # No shares to sell
        self.assertEqual(holding1.shares, 0)  # AAPL unchanged
        self.assertEqual(holding2.shares, 0)  # MSFT unchanged 