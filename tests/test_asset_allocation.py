import unittest
from asset_allocation import AssetClass, AssetClassCategory, Portfolio, Holding
from asset_allocation.quote_service import FakeQuoteService

class TestAssetAllocation(unittest.TestCase):
    def setUp(self):
        # Create a fake quote service with fixed prices
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "TLT": 100.0
        })
        
    def test_portfolio_cash(self):
        portfolio = Portfolio([], cash_value=1000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, None)

        portfolio_with_target = Portfolio([], cash_value=1000.0, cash_target=2000.0)
        self.assertEqual(portfolio_with_target.cash_value, 1000.0)
        self.assertEqual(portfolio_with_target.cash_target, 2000.0)

    def test_holding(self):
        # Test holding
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)
        self.assertEqual(holding.value, 1000.0)  # 10 shares * $100 per share

    def test_asset_class(self):
        # Create some holdings
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        
        # Create an asset class
        asset_class = AssetClass("US Equity", [holding], target_weight=0.4)
        self.assertEqual(asset_class.name, "US Equity")
        self.assertEqual(asset_class.value, 1000.0)
        self.assertEqual(asset_class.target_weight, 0.4)
        self.assertEqual(len(asset_class.children), 1)

        # Test invalid target weights
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_weight=-0.1)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_weight=1.1)

    def test_asset_class_category(self):
        # Create some holdings
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        
        # Create asset classes
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        
        # Create a category containing the asset classes
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        self.assertEqual(equity.name, "Equity")
        self.assertEqual(equity.value, 2000.0)
        self.assertAlmostEqual(equity.target_weight, 0.6)  # Sum of children's weights
        self.assertEqual(len(equity.children), 2)

    def test_portfolio_target_allocation(self):
        # Create some holdings
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        
        # Create asset classes
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.6)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.4)
        
        # Create portfolio with valid weights
        portfolio = Portfolio([us_equity, intl_equity])
        self.assertEqual(portfolio.value, 2000.0)
        
        # Test invalid weights
        invalid_equity = AssetClass("Invalid", [holding1], target_weight=0.3)
        with self.assertRaises(ValueError) as cm:
            Portfolio([invalid_equity, intl_equity])
        self.assertIn("Sum of target weights must be 1.0", str(cm.exception))

    def test_nested_categories(self):
        # Create some holdings
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 10, quote_service=self.quote_service)
        holding3 = Holding("TLT", 20, quote_service=self.quote_service)
        
        # Create asset classes
        us_equity = AssetClass("US Equity", [holding1], target_weight=0.4)
        intl_equity = AssetClass("International Equity", [holding2], target_weight=0.2)
        bonds = AssetClass("Bonds", [holding3], target_weight=0.4)
        
        # Create categories
        equity = AssetClassCategory("Equity", [us_equity, intl_equity])
        fixed_income = AssetClassCategory("Fixed Income", [bonds])
        
        # Create portfolio with categories
        portfolio = Portfolio([equity, fixed_income], cash_value=1000.0, cash_target=2000.0)
        
        # Each holding is worth 1000.0 (10 shares * $100) or 2000.0 (20 shares * $100)
        # Total value should be: 1000.0 (AAPL) + 1000.0 (MSFT) + 2000.0 (TLT) + 1000.0 (cash) = 5000.0
        self.assertEqual(portfolio.value, 5000.0)  # Sum of all holdings
        self.assertEqual(equity.value, 2000.0)  # AAPL + MSFT
        self.assertEqual(fixed_income.value, 2000.0)  # TLT
        self.assertEqual(len(portfolio.children), 2)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)
        self.assertAlmostEqual(equity.target_weight, 0.6)  # Sum of children's weights
        self.assertAlmostEqual(fixed_income.target_weight, 0.4)  # Sum of children's weights

if __name__ == '__main__':
    unittest.main() 