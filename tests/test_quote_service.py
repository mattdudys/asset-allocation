import unittest
from unittest.mock import patch, MagicMock
from asset_allocation.quote_service import (
    YFinanceQuoteService,
    FakeQuoteService,
    BatchYFinanceQuoteService,
)
import pandas as pd


class TestYFinanceQuoteService(unittest.TestCase):
    """Tests for the YFinanceQuoteService implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = YFinanceQuoteService()

    @patch("yfinance.Ticker")
    def test_get_price_uses_cache(self, mock_ticker):
        """Test that get_price uses the cached info dictionary."""
        # Mock the Ticker.info dictionary
        mock_info = {"regularMarketPrice": 100.0, "bid": 99.5, "ask": 100.5}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        # First call should fetch from yfinance
        price = self.service.get_price("VTI")
        self.assertEqual(price, 100.0)
        mock_ticker.assert_called_once_with("VTI")

        # Reset the mock to verify it's not called again
        mock_ticker.reset_mock()

        # Second call should use cache
        price = self.service.get_price("VTI")
        self.assertEqual(price, 100.0)
        mock_ticker.assert_not_called()

    @patch("yfinance.Ticker")
    def test_get_bid_price_uses_cache(self, mock_ticker):
        """Test that get_bid_price uses the cached info dictionary."""
        # Mock the Ticker.info dictionary
        mock_info = {"regularMarketPrice": 100.0, "bid": 99.5, "ask": 100.5}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        # First call should fetch from yfinance
        price = self.service.get_bid_price("VTI")
        self.assertEqual(price, 99.5)
        mock_ticker.assert_called_once_with("VTI")

        # Reset the mock to verify it's not called again
        mock_ticker.reset_mock()

        # Second call should use cache
        price = self.service.get_bid_price("VTI")
        self.assertEqual(price, 99.5)
        mock_ticker.assert_not_called()

    @patch("yfinance.Ticker")
    def test_get_ask_price_uses_cache(self, mock_ticker):
        """Test that get_ask_price uses the cached info dictionary."""
        # Mock the Ticker.info dictionary
        mock_info = {"regularMarketPrice": 100.0, "bid": 99.5, "ask": 100.5}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        # First call should fetch from yfinance
        price = self.service.get_ask_price("VTI")
        self.assertEqual(price, 100.5)
        mock_ticker.assert_called_once_with("VTI")

        # Reset the mock to verify it's not called again
        mock_ticker.reset_mock()

        # Second call should use cache
        price = self.service.get_ask_price("VTI")
        self.assertEqual(price, 100.5)
        mock_ticker.assert_not_called()

    @patch("yfinance.Ticker")
    def test_get_bid_price_missing(self, mock_ticker):
        """Test that get_bid_price raises ValueError when bid price is missing."""
        # Mock the Ticker.info dictionary with missing bid price
        mock_info = {"regularMarketPrice": 100.0}  # No bid price
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        with self.assertRaisesRegex(
            ValueError, "Bid price not available for ticker VTI"
        ):
            self.service.get_bid_price("VTI")

    @patch("yfinance.Ticker")
    def test_get_bid_price_none(self, mock_ticker):
        """Test that get_bid_price raises ValueError when bid price is None."""
        # Mock the Ticker.info dictionary with None bid price
        mock_info = {"bid": None, "regularMarketPrice": 100.0}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        with self.assertRaisesRegex(
            ValueError, "Bid price not available for ticker VTI"
        ):
            self.service.get_bid_price("VTI")

    @patch("yfinance.Ticker")
    def test_get_ask_price_missing(self, mock_ticker):
        """Test that get_ask_price raises ValueError when ask price is missing."""
        # Mock the Ticker.info dictionary with missing ask price
        mock_info = {"regularMarketPrice": 100.0, "bid": 100.0}  # No ask price
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        with self.assertRaisesRegex(
            ValueError, "Ask price not available for ticker VTI"
        ):
            self.service.get_ask_price("VTI")

    @patch("yfinance.Ticker")
    def test_get_ask_price_none(self, mock_ticker):
        """Test that get_ask_price raises ValueError when ask price is None."""
        # Mock the Ticker.info dictionary with None ask price
        mock_info = {"ask": None, "regularMarketPrice": 100.0, "bid": 100.0}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        with self.assertRaisesRegex(
            ValueError, "Ask price not available for ticker VTI"
        ):
            self.service.get_ask_price("VTI")

    @patch("yfinance.Ticker")
    def test_cache_prefetches_info(self, mock_ticker):
        """Test that cache method pre-fetches info for multiple tickers."""
        # Mock the Ticker.info dictionary
        mock_info = {"regularMarketPrice": 100.0, "bid": 99.5, "ask": 100.5}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        # Cache multiple tickers
        self.service.cache(["VTI", "VOO"])

        # Verify Ticker was called for each ticker
        self.assertEqual(mock_ticker.call_count, 2)
        mock_ticker.assert_any_call("VTI")
        mock_ticker.assert_any_call("VOO")

        # Reset the mock to verify it's not called again
        mock_ticker.reset_mock()

        # Verify subsequent calls use cache
        self.service.get_price("VTI")
        self.service.get_bid_price("VTI")
        self.service.get_ask_price("VTI")
        self.service.get_price("VOO")
        self.service.get_bid_price("VOO")
        self.service.get_ask_price("VOO")
        mock_ticker.assert_not_called()


class TestFakeQuoteService(unittest.TestCase):
    """Tests for the FakeQuoteService implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.prices = {
            "VTI": 100.0,
            "VOO": 200.0,
        }
        self.service = FakeQuoteService(self.prices)

    def test_get_price_returns_predefined_price(self):
        """Test that get_price returns the predefined price."""
        self.assertEqual(self.service.get_price("VTI"), 100.0)
        self.assertEqual(self.service.get_price("VOO"), 200.0)

    def test_get_price_raises_keyerror_for_unknown_ticker(self):
        """Test that get_price raises KeyError for unknown ticker."""
        with self.assertRaisesRegex(KeyError, "No price defined for ticker UNKNOWN"):
            self.service.get_price("UNKNOWN")

    def test_get_bid_price_returns_predefined_price(self):
        """Test that get_bid_price returns the predefined price."""
        self.assertEqual(self.service.get_bid_price("VTI"), 100.0)
        self.assertEqual(self.service.get_bid_price("VOO"), 200.0)

    def test_get_bid_price_raises_keyerror_for_unknown_ticker(self):
        """Test that get_bid_price raises KeyError for unknown ticker."""
        with self.assertRaisesRegex(KeyError, "No price defined for ticker UNKNOWN"):
            self.service.get_bid_price("UNKNOWN")

    def test_get_ask_price_returns_predefined_price(self):
        """Test that get_ask_price returns the predefined price."""
        self.assertEqual(self.service.get_ask_price("VTI"), 100.0)
        self.assertEqual(self.service.get_ask_price("VOO"), 200.0)

    def test_get_ask_price_raises_keyerror_for_unknown_ticker(self):
        """Test that get_ask_price raises KeyError for unknown ticker."""
        with self.assertRaisesRegex(KeyError, "No price defined for ticker UNKNOWN"):
            self.service.get_ask_price("UNKNOWN")


yfinance_download_return_value = pd.DataFrame.from_dict(
    {
        ("Close", "VOO"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 541.64},
        ("Close", "VTI"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 100.0},
        ("Bid", "VOO"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 541.64},
        ("Bid", "VTI"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 99.5},
        ("Ask", "VOO"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 541.64},
        ("Ask", "VTI"): {pd.Timestamp("2025-05-30 19:59:00+0000", tz="UTC"): 100.5},
    }
)


@patch("yfinance.download", return_value=yfinance_download_return_value)
class TestBatchYFinanceQuoteService(unittest.TestCase):
    """Tests for the BatchYFinanceQuoteService implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock data in the format returned by yfinance.download
        self.service = BatchYFinanceQuoteService()

    def test_get_prices(self, mock_download):
        """Test that get_price, get_bid_price, and get_ask_price return the correct prices."""
        self.service.cache(["VTI", "VOO"])
        self.assertEqual(self.service.get_price("VTI"), 100.0)
        self.assertEqual(self.service.get_price("VOO"), 541.64)
        self.assertEqual(self.service.get_bid_price("VTI"), 99.5)
        self.assertEqual(self.service.get_bid_price("VOO"), 541.64)
        self.assertEqual(self.service.get_ask_price("VTI"), 100.5)
        self.assertEqual(self.service.get_ask_price("VOO"), 541.64)

    def test_ticker_not_found(self, mock_download):
        """Test that if yfinance.download does not return data for a ticker that we get an error."""
        with self.assertRaisesRegex(
            KeyError, "Could not load data for tickers: UNKNOWN"
        ):
            self.service.get_price("UNKNOWN")
