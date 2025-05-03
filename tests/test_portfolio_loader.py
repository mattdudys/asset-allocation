import unittest
from asset_allocation.portfolio_loader import load_portfolio
from asset_allocation.quote_service import FakeQuoteService

class TestPortfolioLoader(unittest.TestCase):
    def setUp(self):
        # Create a fake quote service with fixed prices for all test tickers
        self.quote_service = FakeQuoteService({
            "AAPL": 100.0,
            "MSFT": 100.0,
            "GOOGL": 100.0,
            "SAP": 100.0,
            "ASML": 100.0,
            "AGG": 100.0,
            "BND": 100.0,
            "BNDX": 100.0,
            "BWX": 100.0
        })

    def test_load_portfolio(self):
        portfolio = load_portfolio(
            'data/portfolio_hierarchy.yaml',
            'data/portfolio_holdings.yaml',
            self.quote_service
        )
        
        # Test basic portfolio properties
        self.assertEqual(portfolio.cash_value, 10000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)
        
        # Test that all holdings were loaded
        total_holdings = 0
        for investment in portfolio.investments.children:
            if hasattr(investment, 'holdings'):
                total_holdings += len(investment.holdings)
            elif hasattr(investment, 'children'):
                for child in investment.children:
                    total_holdings += len(child.holdings)
        
        self.assertEqual(total_holdings, 9)  # Total number of holdings in our test data

if __name__ == '__main__':
    unittest.main() 