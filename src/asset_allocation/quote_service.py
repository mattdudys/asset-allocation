from abc import ABC, abstractmethod
import yfinance


class QuoteService(ABC):
    """Interface for getting stock quotes."""

    @abstractmethod
    def get_price(self, ticker: str) -> float:
        """Get the current price for a ticker symbol."""
        pass

    def cache(self, tickers: list[str]) -> None:
        """A hint to the quote service to cache the prices of the tickers."""
        pass


class YFinanceQuoteService(QuoteService):
    """Real quote service that uses yfinance."""

    def get_price(self, ticker: str) -> float:
        """Get the current price using yfinance."""
        return yfinance.Ticker(ticker).info["regularMarketPrice"]


class BatchYFinanceQuoteService(QuoteService):
    """Real quote service that uses yfinance. Tickers need to be known in advance."""

    _prices: dict[str, float] = {}

    def get_price(self, ticker: str) -> float:
        """Get the current price using yfinance."""
        if ticker not in self._prices:
            raise KeyError(f"No price found for ticker {ticker}")
        return self._prices[ticker]

    def cache(self, tickers: list[str]) -> None:
        self._prices = (
            yfinance.download(
                tickers,
                period="1d",
                interval="1m",
                progress=False,
                auto_adjust=True,
            )
            .ffill()["Close"]
            .iloc[-1]
        )


class FakeQuoteService(QuoteService):
    """Fake quote service for testing with predefined prices."""

    def __init__(self, prices: dict[str, float]):
        """Initialize with a dictionary mapping ticker symbols to prices."""
        self.prices = prices

    def get_price(self, ticker: str) -> float:
        """Get the predefined price for a ticker symbol."""
        if ticker not in self.prices:
            raise KeyError(f"No price defined for ticker {ticker}")
        return self.prices[ticker]
