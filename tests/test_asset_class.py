import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import AssetClass, CompositeAssetClass, LeafAssetClass


class TestAssetClass(unittest.TestCase):
    def test_asset_class_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])

        self.assertEqual(asset_class.name, "US Equity")
        self.assertEqual(asset_class.target_weight, 0.4)
        self.assertEqual(len(asset_class.children), 1)

    def test_asset_class_value_sums_holdings(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 5, price=300.0)
        asset_class = LeafAssetClass(
            "US Equity", target_weight=0.4, children=[holding1, holding2]
        )
        self.assertEqual(
            asset_class.value, 1000.0 + 1500.0
        )  # 10 shares * $100 + 5 shares * $300

    def test_asset_class_actual_weight_when_overweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # Value is 1000, portfolio is 2000, so weight is 0.5 (25% overweight)
        self.assertEqual(asset_class.actual_weight(2000.0), 0.5)

    def test_asset_class_actual_weight_when_underweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # Value is 1000, portfolio is 4000, so weight is 0.25 (37.5% underweight)
        self.assertEqual(asset_class.actual_weight(4000.0), 0.25)

    def test_asset_class_actual_weight_when_balanced(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # Value is 1000, portfolio is 2500, so weight is 0.4 (perfectly balanced)
        self.assertEqual(asset_class.actual_weight(2500.0), 0.4)

    def test_asset_class_fractional_deviation_when_overweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # (0.5/0.4) - 1 = 0.25 (25% overweight)
        self.assertEqual(asset_class.fractional_deviation(2000.0), 0.25)

    def test_asset_class_fractional_deviation_when_underweight(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # (0.25/0.4) - 1 = -0.375 (37.5% underweight)
        self.assertEqual(asset_class.fractional_deviation(4000.0), -0.375)

    def test_asset_class_fractional_deviation_when_balanced(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # (0.4/0.4) - 1 = 0.0 (perfectly balanced)
        self.assertEqual(asset_class.fractional_deviation(2500.0), 0.0)

    def test_asset_class_rejects_negative_target_weight(self):
        holding = Holding("AAPL", 10, price=100.0)
        with self.assertRaises(ValueError):
            LeafAssetClass("Invalid", target_weight=-0.1, children=[holding])

    def test_asset_class_rejects_target_weight_over_one(self):
        holding = Holding("AAPL", 10, price=100.0)
        with self.assertRaises(ValueError):
            LeafAssetClass("Invalid", target_weight=1.1, children=[holding])

    def test_asset_class_rejects_empty_holdings(self):
        with self.assertRaises(ValueError) as cm:
            LeafAssetClass("Invalid", target_weight=0.4, children=[])
        self.assertEqual(str(cm.exception), "AssetClass must have at least one holding")

    def test_asset_class_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        with self.assertRaises(ValueError):
            asset_class.actual_weight(0.0)

    def test_asset_class_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        with self.assertRaises(ValueError):
            asset_class.actual_weight(-1000.0)

    def test_asset_class_buy_with_sufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        transaction = asset_class.buy(150.0, 2500.0)
        self.assertIsNotNone(transaction)
        self.assertEqual(holding.shares, 11)

    def test_asset_class_buy_with_insufficient_budget(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        transaction = asset_class.buy(50.0, 2500.0)
        self.assertIsNone(transaction)
        self.assertEqual(holding.shares, 10)

    def test_asset_class_buy_with_multiple_holdings(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        transaction = asset_class.buy(150.0, 2500.0)
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 11)  # First holding should be bought
        self.assertEqual(holding2.shares, 10)  # Second holding should be unchanged

    def test_asset_class_sell_from_last_holding(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        transaction = asset_class.sell()
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 10)  # First holding unchanged
        self.assertEqual(holding2.shares, 9)  # Second holding reduced by 1

    def test_asset_class_sell_from_last_holding_fractional(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 0.5, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        transaction = asset_class.sell()
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 10)  # First holding unchanged
        self.assertEqual(holding2.shares, 0)  # Second holding reduced to 0

    def test_asset_class_sell_from_second_last_when_last_empty(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        transaction = asset_class.sell()
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 9)  # First holding reduced by 1
        self.assertEqual(holding2.shares, 0)  # Second holding unchanged

    def test_asset_class_sell_returns_zero_when_all_empty(self):
        holding1 = Holding("AAPL", 0, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        transaction = asset_class.sell()
        self.assertIsNone(transaction)
        self.assertEqual(holding1.shares, 0)  # First holding unchanged
        self.assertEqual(holding2.shares, 0)  # Second holding unchanged

    def test_asset_class_with_multiple_holdings(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        asset_class = LeafAssetClass(
            "Tech", target_weight=0.6, children=[holding1, holding2]
        )

        self.assertEqual(asset_class.value, 2000.0)  # 1000 + 1000
        self.assertEqual(asset_class.actual_weight(4000.0), 0.5)  # 2000/4000 = 0.5

    def test_asset_class_rebalance_band_large(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        self.assertEqual(asset_class.rebalance_band, 0.05)

    def test_asset_class_rebalance_band_small(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.1, children=[holding])
        self.assertEqual(asset_class.rebalance_band, 0.025)  # 0.1 * 0.25 = 0.025

    def test_asset_class_overweight_true(self):
        holding = Holding("AAPL", 50, price=100.0)  # 5000
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # Upper bound is 40% + 5% = 45%
        # 5000/10000 = 50% > 45%, overweight
        self.assertEqual(asset_class.rebalance_band, 0.05)
        self.assertTrue(
            asset_class.overweight(10000.0),
            "50% is considered overweight when target is 40%",
        )

    def test_asset_class_overweight_false(self):
        holding = Holding("AAPL", 43, price=100.0)  # 4300
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        # Upper bound is 40% + 5% = 45%
        # 4300/10000 = 43% < 45%, not overweight
        self.assertFalse(
            asset_class.overweight(10000.0),
            "43% is not considered overweight when target is 40%",
        )

    def test_asset_class_underweight_true(self):
        holding = Holding("VWO", 4, price=100.0)  # 400
        asset_class = LeafAssetClass(
            "Emerging Markets", target_weight=0.06, children=[holding]
        )
        # Lower bound is 6% - (25% * 6%) = 4.5%
        # 400/10000 = 4% < 4.5%, underweight
        self.assertTrue(
            asset_class.underweight(10000.0),
            "4% is considered underweight when target is 6%",
        )

    def test_asset_class_underweight_false(self):
        holding = Holding("VWO", 5, price=100.0)  # 500
        asset_class = LeafAssetClass(
            "Emerging Markets", target_weight=0.06, children=[holding]
        )
        # Lower bound is 6% - (25% * 6%) = 4.5%
        # 500/10000 = 5% > 4.5%, not underweight
        self.assertFalse(
            asset_class.underweight(10000.0),
            "5% is not considered underweight when target is 6%",
        )


class TestCompositeAssetClass(unittest.TestCase):
    def test_composite_creation_sets_basic_properties(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        composite = CompositeAssetClass("Equity", [asset_class])

        self.assertEqual(composite.name, "Equity")
        self.assertEqual(len(composite.children), 1)

    def test_composite_rejects_empty_children(self):
        with self.assertRaises(ValueError) as cm:
            CompositeAssetClass("Invalid", [])
        self.assertEqual(
            str(cm.exception), "CompositeAssetClass must have at least one child"
        )

    def test_composite_value_sums_children(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        self.assertEqual(composite.value, 2000.0)  # 1000 + 1000
        self.assertAlmostEqual(composite.target_weight, 0.6)  # 0.4 + 0.2

    def test_composite_actual_weight_when_underweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # Value is 2000, portfolio is 4000, so weight is 0.5 (16.7% underweight)
        self.assertEqual(composite.actual_weight(4000.0), 0.5)

    def test_composite_actual_weight_when_overweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # Value is 2000, portfolio is 3000, so weight is 0.667 (11.1% overweight)
        self.assertAlmostEqual(composite.actual_weight(3000.0), 0.667, places=3)

    def test_composite_actual_weight_when_balanced(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # Value is 2000, portfolio is 3333.33, so weight is 0.6 (perfectly balanced)
        self.assertAlmostEqual(composite.actual_weight(3333.33), 0.6, places=2)

    def test_composite_fractional_deviation_when_underweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # (0.5/0.6) - 1 = -0.167 (16.7% underweight)
        self.assertAlmostEqual(composite.fractional_deviation(4000.0), -0.167, places=3)

    def test_composite_fractional_deviation_when_overweight(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # (0.667/0.6) - 1 = 0.111 (11.1% overweight)
        self.assertAlmostEqual(composite.fractional_deviation(3000.0), 0.111, places=3)

    def test_composite_fractional_deviation_when_balanced(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # (0.6/0.6) - 1 = 0.0 (perfectly balanced)
        self.assertAlmostEqual(composite.fractional_deviation(3333.33), 0.0, places=2)

    def test_composite_rejects_zero_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        composite = CompositeAssetClass("Equity", [asset_class])
        with self.assertRaises(ValueError):
            composite.actual_weight(0.0)

    def test_composite_rejects_negative_portfolio_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        composite = CompositeAssetClass("Equity", [asset_class])
        with self.assertRaises(ValueError):
            composite.actual_weight(-1000.0)

    def test_nested_composites(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        equity = CompositeAssetClass("Equity", [us_equity, intl_equity])

        holding3 = Holding("AGG", 10, price=100.0)
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = CompositeAssetClass("Total", [equity, fixed_income])

        self.assertEqual(portfolio.value, 3000.0)  # 1000 + 1000 + 1000
        self.assertEqual(portfolio.target_weight, 1.0)  # 0.6 + 0.4

    def test_composite_sell_from_most_overweight(self):
        # Create holdings with different weights
        holding1 = Holding("AAPL", 10, price=100.0)  # 1000
        holding2 = Holding("MSFT", 10, price=100.0)  # 1000
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # US Equity is overweight (0.4/0.4 = 1.0), Intl Equity is overweight (0.4/0.2 = 2.0)
        transaction = composite.sell(2000.0)
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 10)  # AAPL unchanged
        self.assertEqual(holding2.shares, 9)  # MSFT reduced by 1

    def test_composite_sell_from_second_most_overweight(self):
        # Create holdings with different weights
        holding1 = Holding("AAPL", 10, price=100.0)  # 1000
        holding2 = Holding("MSFT", 0, price=100.0)  # 0
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        # US Equity is overweight (0.4/0.4 = 1.0), Intl Equity is empty
        transaction = composite.sell(1000.0)
        self.assertIsNotNone(transaction)
        self.assertEqual(holding1.shares, 9)  # AAPL reduced by 1
        self.assertEqual(holding2.shares, 0)  # MSFT unchanged

    def test_composite_sell_returns_zero_when_all_empty(self):
        holding1 = Holding("AAPL", 0, price=100.0)
        holding2 = Holding("MSFT", 0, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        composite = CompositeAssetClass("Equity", [us_equity, intl_equity])

        transaction = composite.sell(1000.0)  # Using a positive portfolio value
        self.assertIsNone(transaction)
        self.assertEqual(holding1.shares, 0)  # AAPL unchanged
        self.assertEqual(holding2.shares, 0)  # MSFT unchanged
