import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import AssetClass, AssetClassCategory
from asset_allocation.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):
    def test_empty_portfolio_creation(self):
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[])
        self.assertEqual(str(cm.exception), "Portfolio must have at least one asset class or category")

    def test_portfolio_with_cash_target(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=1.0, holdings=[holding])
        portfolio = Portfolio(cash_value=1000.0, cash_target=0.2, children=[asset_class])
        
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 0.2)

    def test_portfolio_value_sums_children_and_cash(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=1.0, holdings=[holding])
        portfolio = Portfolio(cash_value=1000.0, children=[asset_class])
        
        self.assertEqual(portfolio.value, 2000.0)  # 1000 (cash) + 1000 (holdings)

    def test_portfolio_rejects_invalid_target_weights(self):
        holding = Holding("AAPL", 10, price=100.0)
        asset_class = AssetClass("US Equity", target_weight=0.4, holdings=[holding])
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[asset_class])
        self.assertEqual(str(cm.exception), "Sum of target weights must be 1.0, got 0.4")

    def test_portfolio_with_nested_categories(self):
        holding1 = Holding("AAPL", 10, price=100.0)
        holding2 = Holding("MSFT", 10, price=100.0)
        us_equity = AssetClass("US Equity", target_weight=0.4, holdings=[holding1])
        intl_equity = AssetClass("International Equity", target_weight=0.2, holdings=[holding2])
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        
        holding3 = Holding("AGG", 10, price=100.0)
        fixed_income = AssetClass("Fixed Income", target_weight=0.4, holdings=[holding3])
        
        portfolio = Portfolio(cash_value=1000.0, children=[equity, fixed_income])
        
        self.assertEqual(portfolio.value, 4000.0)  # 1000 (cash) + 3000 (holdings) 