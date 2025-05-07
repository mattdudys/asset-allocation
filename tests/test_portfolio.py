import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import CompositeAssetClass, LeafAssetClass
from asset_allocation.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):
    def test_empty_portfolio_creation(self):
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[])
        self.assertEqual(
            str(cm.exception),
            "Portfolio must have at least one asset class or category",
        )

    def test_portfolio_with_cash_target(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=0.2, children=[asset_class]
        )

        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 0.2)

    def test_portfolio_value_sums_children_and_cash(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(cash_value=1000.0, children=[asset_class])

        self.assertEqual(portfolio.value, 2000.0)  # 1000 (cash) + 1000 (holdings)

    def test_portfolio_rejects_invalid_target_weights(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[asset_class])
        self.assertEqual(
            str(cm.exception), "Sum of target weights must be 1.0, got 0.4"
        )

    def test_portfolio_with_nested_categories(self):
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

        portfolio = Portfolio(cash_value=1000.0, children=[equity, fixed_income])

        self.assertEqual(portfolio.value, 4000.0)  # 1000 (cash) + 3000 (holdings)

    def test_excess_cash_calculation(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        self.assertEqual(portfolio.excess_cash, 500.0)  # 1000 - 500 target

    def test_excess_cash_with_no_target(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=None, children=[asset_class]
        )

        self.assertEqual(
            portfolio.excess_cash, 1000.0
        )  # All cash is excess when no target

    def test_excess_cash_below_target(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=300.0, cash_target=500.0, children=[asset_class]
        )

        self.assertEqual(portfolio.excess_cash, 0.0)  # No excess when below target

    def test_investible_value(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        # investible_value = investments (1000) + excess_cash (500)
        self.assertEqual(portfolio.investible_value, 1500.0)

    def test_invest_excess_cash(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        portfolio.invest_excess_cash()

        # After investing excess cash, cash should be at target
        self.assertEqual(portfolio.cash_value, 500.0)
        # Total value should remain the same (1000 cash + 1000 holdings)
        self.assertEqual(portfolio.value, 2000.0)
        # Holdings value should increase by the amount invested
        self.assertEqual(portfolio.investments.value, 1500.0)

    def test_invest_excess_cash_with_no_target(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=None, children=[asset_class]
        )

        portfolio.invest_excess_cash()

        # All cash should be invested when no target
        self.assertEqual(portfolio.cash_value, 0.0)
        # Total value should remain the same
        self.assertEqual(portfolio.value, 2000.0)
