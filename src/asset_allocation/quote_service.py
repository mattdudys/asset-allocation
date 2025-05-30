from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import yfinance
from .price_validation import validate_prices


class QuoteService(ABC):
    """Interface for getting stock quotes.

    This interface provides methods to get current market price, bid price, and ask price
    for a given ticker symbol. The bid price represents the highest price a buyer is willing
    to pay, while the ask price represents the lowest price a seller is willing to accept.
    """

    @abstractmethod
    def get_price(self, ticker: str) -> float:
        """Get the current market price for a ticker symbol.

        Args:
            ticker: The ticker symbol to get the price for

        Returns:
            The current market price
        """
        pass

    @abstractmethod
    def get_bid_price(self, ticker: str) -> float:
        """Get the current bid price for a ticker symbol.

        The bid price is the highest price a buyer is willing to pay for the security.

        Args:
            ticker: The ticker symbol to get the bid price for

        Returns:
            The current bid price

        Raises:
            ValueError: If the bid price is not available
        """
        pass

    @abstractmethod
    def get_ask_price(self, ticker: str) -> float:
        """Get the current ask price for a ticker symbol.

        The ask price is the lowest price a seller is willing to accept for the security.

        Args:
            ticker: The ticker symbol to get the ask price for

        Returns:
            The current ask price

        Raises:
            ValueError: If the ask price is not available
        """
        pass

    def cache(self, tickers: list[str]) -> None:
        """A hint to the quote service to cache the prices of the tickers."""
        pass


class YFinanceQuoteService(QuoteService):
    """Real quote service that uses yfinance."""

    def __init__(self):
        """Initialize the quote service with an empty cache."""
        self._info_cache: dict[str, dict] = {}

    def _get_ticker_info(self, ticker: str) -> dict:
        """Get the ticker info dictionary, using cache if available.

        Args:
            ticker: The ticker symbol to get info for

        Returns:
            The ticker info dictionary with validated prices
        """
        if ticker not in self._info_cache:
            info = yfinance.Ticker(ticker).info

            # Validate that required price data exists
            if "regularMarketPrice" not in info or not isinstance(
                info["regularMarketPrice"], float
            ):
                raise ValueError(f"Price not available for ticker {ticker}")
            if "bid" not in info or not isinstance(info["bid"], float):
                raise ValueError(f"Bid price not available for ticker {ticker}")
            if "ask" not in info or not isinstance(info["ask"], float):
                raise ValueError(f"Ask price not available for ticker {ticker}")

            # Validate price relationships
            validate_prices(
                ticker,
                info["regularMarketPrice"],
                bid_price=info["bid"],
                ask_price=info["ask"],
            )

            self._info_cache[ticker] = info
        return self._info_cache[ticker]

    def get_price(self, ticker: str) -> float:
        """Get the current price using yfinance.

        The price is retrieved from the 'regularMarketPrice' key in the ticker info dictionary.
        If the price is not available, a ValueError is raised.

        Args:
            ticker: The ticker symbol to get the price for

        Returns:
            The current market price
        """
        return self._get_ticker_info(ticker)["regularMarketPrice"]

    def get_bid_price(self, ticker: str) -> float:
        """Get the current bid price using yfinance.

        The bid price is retrieved from the 'bid' key in the ticker info dictionary.
        If the bid price is not available, a ValueError is raised.

        Args:
            ticker: The ticker symbol to get the bid price for

        Returns:
            The current bid price
        """
        return self._get_ticker_info(ticker)["bid"]

    def get_ask_price(self, ticker: str) -> float:
        """Get the current ask price using yfinance.

        The ask price is retrieved from the 'ask' key in the ticker info dictionary.
        If the ask price is not available, a ValueError is raised.

        Args:
            ticker: The ticker symbol to get the ask price for

        Returns:
            The current ask price

        Raises:
            ValueError: If the ask price is not available in the ticker info
        """
        return self._get_ticker_info(ticker)["ask"]

    def cache(self, tickers: list[str]) -> None:
        """Pre-fetch and cache the info for the given tickers."""
        for ticker in tickers:
            self._get_ticker_info(ticker)


class BatchYFinanceQuoteService(QuoteService):
    """Real quote service that uses yfinance. Tickers need to be known in advance."""

    _data: pd.DataFrame | None = None

    def cache(self, tickers: list[str]) -> None:
        """Load the data for the given tickers."""
        # If self._data is not None and all tickers are in it, return.
        if self._data is not None and all(ticker in self._data for ticker in tickers):
            return

        # Otherwise, load the data.
        data = yfinance.download(
            tickers,
            period="1d",
            interval="1m",
            progress=False,
            auto_adjust=True,
            rounding=True,
        ).ffill()
        if data.empty:
            raise KeyError(f"Could not load data for tickers: {','.join(tickers)}")

        # Get the most recent minute, unstack and transpose to Close/Bid/Ask columns and ticker rows.
        data = data.iloc[-1].unstack().T

        # If self._data is None, set it to the new data.
        # Otherwise, combine the new data with the existing data.
        if self._data is None:
            self._data = data
        else:
            self._data = data.combine_first(self._data)

        # Validate that the data now has all the tickers.
        missing_tickers = set([])
        for ticker in tickers:
            if ticker not in self._data.index:
                missing_tickers.add(ticker)
        if missing_tickers:
            raise KeyError(
                f"Could not load data for tickers: {','.join(missing_tickers)}"
            )

        # Validate prices for all tickers
        for ticker in tickers:
            if ticker in self._data.index:
                market_price = self._data["Close"][ticker]
                bid_price = self._data.get("Bid", {}).get(ticker)
                ask_price = self._data.get("Ask", {}).get(ticker)
                validate_prices(ticker, market_price, bid_price, ask_price)

    def get_price(self, ticker: str) -> float:
        """Get the current price using yfinance."""
        self.cache([ticker])
        return self._data["Close"][ticker]

    def get_bid_price(self, ticker: str) -> float:
        """Get the current bid price using yfinance."""
        self.cache([ticker])
        return self._data["Bid"][ticker]

    def get_ask_price(self, ticker: str) -> float:
        """Get the current ask price using yfinance."""
        self.cache([ticker])
        return self._data["Ask"][ticker]


class FakeQuoteService(QuoteService):
    """Fake quote service for testing with predefined prices."""

    def __init__(
        self,
        prices: dict[str, float],
        bids: Optional[dict[str, float]] = None,
        asks: Optional[dict[str, float]] = None,
    ):
        """Initialize with a dictionary mapping ticker symbols to prices."""
        self.prices = prices
        self.bids = bids if bids else {}
        self.asks = asks if asks else {}

    def get_price(self, ticker: str) -> float:
        """Get the predefined price for a ticker symbol."""
        if ticker not in self.prices:
            raise KeyError(f"No price defined for ticker {ticker}")
        return self.prices[ticker]

    def get_bid_price(self, ticker: str) -> float:
        """Get the predefined price as bid price for a ticker symbol."""
        if ticker not in self.bids:
            return self.get_price(ticker)
        return self.bids[ticker]

    def get_ask_price(self, ticker: str) -> float:
        """Get the predefined price as ask price for a ticker symbol."""
        if ticker not in self.asks:
            return self.get_price(ticker)
        return self.asks[ticker]
