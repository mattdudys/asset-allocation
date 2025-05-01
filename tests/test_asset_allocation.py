import unittest
from unittest.mock import Mock, patch
import yfinance
from asset_allocation import Graph, Node, LeafNode, InternalNode, AssetClass, CashHolding, TickerHolding

class TestAssetAllocation(unittest.TestCase):
    def setUp(self):
        # Create a mock for yfinance.Ticker
        self.mock_ticker = Mock(spec=yfinance.Ticker)
        self.mock_ticker.info = {'regularMarketPrice': 100.0}
        
    def test_cash_holding(self):
        cash = CashHolding(1000.0)
        self.assertEqual(cash.name, "Cash")
        self.assertEqual(cash.value, 1000.0)
        self.assertEqual(cash.target_value, None)
        self.assertEqual(cash.children, [])

        cash_with_target = CashHolding(1000.0, target_value=2000.0)
        self.assertEqual(cash_with_target.target_value, 2000.0)

    @patch('yfinance.Ticker')
    def test_ticker_holding(self, mock_ticker_class):
        # Setup mock
        mock_ticker_class.return_value = self.mock_ticker
        
        # Test ticker holding
        ticker = TickerHolding("AAPL", 10)
        self.assertEqual(ticker.name, "AAPL")
        self.assertEqual(ticker.shares, 10)
        self.assertEqual(ticker.value, 1000.0)  # 10 shares * $100 per share
        self.assertEqual(ticker.children, [])

    def test_internal_node(self):
        # Create leaf nodes
        cash = CashHolding(1000.0)
        
        # Create internal node with children
        internal = InternalNode("Test Group", [cash])
        self.assertEqual(internal.name, "Test Group")
        self.assertEqual(internal.value, 1000.0)
        self.assertEqual(len(internal.children), 1)

    def test_holding_group(self):
        # Create some holdings
        cash = CashHolding(1000.0)
        
        # Create an asset class
        group = AssetClass("Equity", [cash], target_allocation=60)
        self.assertEqual(group.name, "Equity")
        self.assertEqual(group.value, 1000.0)
        self.assertEqual(group.target_allocation, 60)
        self.assertEqual(len(group.children), 1)

        # Test invalid target allocations
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [cash], target_allocation=-10)
        with self.assertRaises(ValueError):
            AssetClass("Invalid", [cash], target_allocation=110)

    def test_nested_groups(self):
        # Create a nested structure
        cash = CashHolding(1000.0)
        bonds = CashHolding(2000.0)
        
        # Create nested groups
        fixed_income = AssetClass("Fixed Income", [bonds], target_allocation=40)
        portfolio = AssetClass("Portfolio", [cash, fixed_income], target_allocation=100)
        
        self.assertEqual(portfolio.value, 3000.0)  # Sum of all holdings
        self.assertEqual(fixed_income.value, 2000.0)
        self.assertEqual(len(portfolio.children), 2)
        self.assertEqual(portfolio.target_allocation, 100)
        self.assertEqual(fixed_income.target_allocation, 40)

if __name__ == '__main__':
    unittest.main() 