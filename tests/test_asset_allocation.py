import unittest
from asset_allocation import Graph, Node, LeafNode, InternalNode, AssetClass, Portfolio, Holding
from asset_allocation.quote_service import FakeQuoteService

class TestAssetAllocation(unittest.TestCase):
    def setUp(self):
        # Create a fake quote service with fixed prices
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0
        })
        
    def test_portfolio_cash(self):
        portfolio = Portfolio("Test Portfolio", [], cash_value=1000.0)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, None)

        portfolio_with_target = Portfolio("Test Portfolio", [], cash_value=1000.0, cash_target=2000.0)
        self.assertEqual(portfolio_with_target.cash_value, 1000.0)
        self.assertEqual(portfolio_with_target.cash_target, 2000.0)

    def test_holding(self):
        # Test holding
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        self.assertEqual(holding.name, "AAPL")
        self.assertEqual(holding.shares, 10)
        self.assertEqual(holding.value, 1000.0)  # 10 shares * $100 per share
        self.assertEqual(holding.children, [])

    def test_internal_node(self):
        # Create leaf nodes
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        
        # Create internal node with children
        internal = InternalNode("Test Group", [holding])
        self.assertEqual(internal.name, "Test Group")
        self.assertEqual(internal.value, 1000.0)
        self.assertEqual(len(internal.children), 1)

    def test_holding_group(self):
        # Create some holdings
        holding = Holding("AAPL", 10, quote_service=self.quote_service)
        
        # Create an asset class
        group = AssetClass("Equity", [holding], target_allocation=60)
        self.assertEqual(group.name, "Equity")
        self.assertEqual(group.value, 1000.0)
        self.assertEqual(group.target_allocation, 60)
        self.assertEqual(len(group.children), 1)

        # Test invalid target allocations
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_allocation=-10)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [holding], target_allocation=110)

    def test_nested_groups(self):
        # Create a nested structure
        holding1 = Holding("AAPL", 10, quote_service=self.quote_service)
        holding2 = Holding("MSFT", 20, quote_service=self.quote_service)
        
        # Create nested groups
        fixed_income = AssetClass("Fixed Income", [holding2], target_allocation=40)
        portfolio = Portfolio("Portfolio", [holding1, fixed_income], cash_value=1000.0, cash_target=2000.0)
        
        self.assertEqual(portfolio.value, 3000.0)  # Sum of all holdings
        self.assertEqual(fixed_income.value, 2000.0)
        self.assertEqual(len(portfolio.children), 2)
        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)
        self.assertEqual(fixed_income.target_allocation, 40)

if __name__ == '__main__':
    unittest.main() 