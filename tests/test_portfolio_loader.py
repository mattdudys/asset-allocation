import unittest
from asset_allocation.portfolio_loader import PortfolioLoader
from asset_allocation.quote_service import FakeQuoteService


class TestPortfolioLoader(unittest.TestCase):
    def setUp(self):
        # Create a fake quote service with fixed prices for all test tickers
        self.quote_service = FakeQuoteService(
            {
                "AAPL": 100.0,
                "MSFT": 100.0,
                "GOOGL": 100.0,
                "SAP": 100.0,
                "ASML": 100.0,
                "AGG": 100.0,
                "BND": 100.0,
                "BNDX": 100.0,
                "BWX": 100.0,
            }
        )
        self.loader = PortfolioLoader(self.quote_service)

    def test_load_portfolio(self):
        portfolio = self.loader.load(
            "data/portfolio_config.yaml",
            "data/portfolio_holdings.yaml",
        )

        # Test basic portfolio properties
        self.assertEqual(portfolio.cash_value, 10000.0)
        self.assertEqual(portfolio.cash_target, 2000.0)

        # Test that all holdings were loaded
        self.assertEqual(len(portfolio.investments.holdings), 9)


if __name__ == "__main__":
    unittest.main()
