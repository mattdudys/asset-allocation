from abc import ABC, abstractmethod
import yfinance


class QuoteService(ABC):
    """Interface for getting stock quotes."""

    @abstractmethod
    def get_price(self, ticker: str) -> float:
        """Get the current price for a ticker symbol."""
        pass


class YFinanceQuoteService(QuoteService):
    """Real quote service that uses yfinance."""

    def get_price(self, ticker: str) -> float:
        """Get the current price using yfinance."""
        return yfinance.Ticker(ticker).info["regularMarketPrice"]


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
