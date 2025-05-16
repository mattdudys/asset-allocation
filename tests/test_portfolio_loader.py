import unittest
from asset_allocation.portfolio_loader import PortfolioLoader
from asset_allocation.quote_service import FakeQuoteService


class TestPortfolioLoader(unittest.TestCase):
    def setUp(self):
        # Create a fake quote service with fixed prices for all tickers referenced in the config
        self.quote_service = FakeQuoteService(
            {
                # Tickers directly held in the portfolio
                "VOO": 100.0,
                "VIOV": 100.0,
                "FNILX": 100.0,
                "VYMI": 100.0,
                "VSS": 100.0,
                "VGIT": 100.0,
                "SUB": 100.0,
                "VTEB": 100.0,
                # Additional tickers referenced in asset classes but not directly held
                "FISVX": 100.0,
                "EFV": 100.0,
                "FNDC": 100.0,
                "BND": 100.0,
            }
        )
        self.loader = PortfolioLoader(self.quote_service)

    def test_load_portfolio(self):
        portfolio = self.loader.load("data/portfolio_config.yaml")

        # Test basic portfolio properties
        self.assertEqual(portfolio.cash_value, 2018.49)
        self.assertEqual(portfolio.cash_target, 2000.0)

        # Test that all holdings were loaded (count unique tickers used in holdings)
        all_holdings = portfolio.investments.holdings
        self.assertGreaterEqual(
            len(all_holdings), 8
        )  # At least 8 holdings from the config


if __name__ == "__main__":
    unittest.main()
