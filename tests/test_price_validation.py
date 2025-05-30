"""Tests for price validation system."""

import unittest
import warnings
from asset_allocation.price_validation import validate_prices


class TestPriceValidation(unittest.TestCase):
    """Test cases for price validation."""

    warnings: list[str]

    def setUp(self):
        """Set up test cases."""
        # Reset warnings registry to ensure clean state for each test
        warnings.resetwarnings()
        # Capture warnings
        self.warnings = []
        warnings.showwarning = lambda *args, **kwargs: self.warnings.append(
            str(args[0])
        )

    def test_valid_prices(self):
        """Test that valid prices don't trigger warnings."""
        validate_prices("AAPL", 100.0, 99.0, 101.0)
        self.assertEqual(len(self.warnings), 0)

    def test_bid_higher_than_ask(self):
        """Test warning when bid is higher than ask."""
        validate_prices("AAPL", 100.0, 101.0, 99.0)
        self.assertIn(
            "Bid price (101.00) is higher than ask price (99.00) for AAPL",
            self.warnings,
        )

    def test_bid_higher_than_market(self):
        """Test warning when bid is higher than market price."""
        validate_prices("AAPL", 100.0, 101.0)
        self.assertIn(
            "Bid price (101.00) is higher than market price (100.00) for AAPL",
            self.warnings,
        )

    def test_ask_lower_than_market(self):
        """Test warning when ask is lower than market price."""
        validate_prices("AAPL", 100.0, ask_price=99.0)
        self.assertIn(
            "Ask price (99.00) is lower than market price (100.00) for AAPL",
            self.warnings,
        )

    def test_large_spread(self):
        """Test warning when spread is larger than 5%."""
        validate_prices("AAPL", 100.0, 95.0, 105.0)  # 10% spread
        self.assertIn(
            "Large spread detected for AAPL: 10.0% (bid: 95.00, ask: 105.00, market: 100.00)",
            self.warnings,
        )

    def test_multiple_warnings(self):
        """Test that multiple issues trigger multiple warnings."""
        validate_prices(
            "AAPL", 100.0, 105.0, 95.0
        )  # Bid > market, ask < market, large spread
        self.assertIn(
            "Bid price (105.00) is higher than ask price (95.00) for AAPL",
            self.warnings,
        )
        self.assertIn(
            "Bid price (105.00) is higher than market price (100.00) for AAPL",
            self.warnings,
        )
        self.assertIn(
            "Ask price (95.00) is lower than market price (100.00) for AAPL",
            self.warnings,
        )
        self.assertIn(
            "Large spread detected for AAPL: 10.0% (bid: 105.00, ask: 95.00, market: 100.00)",
            self.warnings,
        )


if __name__ == "__main__":
    unittest.main()
