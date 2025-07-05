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

    def test_load_portfolio_from_file(self):
        portfolio = self.loader.load_from_file("data/portfolio_config.yaml")

        # Test basic portfolio properties
        self.assertEqual(portfolio.cash_value, 2018.49)
        self.assertEqual(portfolio.cash_target, 2000.0)

        # Test that all holdings were loaded (count unique tickers used in holdings)
        all_holdings = portfolio.investments.holdings
        self.assertGreaterEqual(
            len(all_holdings), 8
        )  # At least 8 holdings from the config

    def test_load_portfolio_from_string(self):
        yaml_string = """
        cash_value: 100.0
        cash_target: 50.0
        holdings:
          VOO: 10
          BND: 5
        asset_classes:
          - name: Equity
            target_weight: 0.6
            holdings: [\"VOO\"]
          - name: Fixed Income
            target_weight: 0.4
            holdings: [\"BND\"]
        """
        portfolio = self.loader.load_from_string(yaml_string)

        self.assertEqual(portfolio.cash_value, 100.0)
        self.assertEqual(portfolio.cash_target, 50.0)
        all_holdings = portfolio.investments.holdings
        self.assertEqual(len(all_holdings), 2)
        tickers = sorted([h.ticker for h in all_holdings])
        self.assertEqual(tickers, ["BND", "VOO"])
        shares = {h.ticker: h.shares for h in all_holdings}
        self.assertEqual(shares["VOO"], 10)
        self.assertEqual(shares["BND"], 5)
        # Check asset class names and weights
        asset_classes = portfolio.investments.children
        self.assertEqual(len(asset_classes), 2)
        names = sorted([ac.name for ac in asset_classes])
        self.assertEqual(names, ["Equity", "Fixed Income"])
        weights = {ac.name: ac.target_weight for ac in asset_classes}
        self.assertAlmostEqual(weights["Equity"], 0.6)
        self.assertAlmostEqual(weights["Fixed Income"], 0.4)


if __name__ == "__main__":
    unittest.main()
