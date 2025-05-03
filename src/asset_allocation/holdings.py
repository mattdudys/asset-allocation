from .quote_service import QuoteService, YFinanceQuoteService
from typing import Union

class Portfolio:
    """A portfolio of holdings."""
    cash_value: float
    cash_target: float | None

    def __init__(self, children: list[Union['AssetClass', 'AssetClassCategory']], cash_value: float = 0.0, cash_target: float | None = None):
        self.children = children
        self.cash_value = cash_value
        self.cash_target = cash_target
        if children:  # Only validate if there are children
            self._validate_target_weights()

    def _validate_target_weights(self):
        """Validate that the sum of target weights is 1.0."""
        total_weight = sum(child.target_weight for child in self.children)
        if not abs(total_weight - 1.0) < 0.001:  # Using small epsilon for float comparison
            raise ValueError(f"Sum of target weights must be 1.0, got {total_weight}")

    @property
    def value(self):
        return sum(child.value for child in self.children) + self.cash_value

class AssetClassCategory:
    """A category that can contain other asset classes or categories."""
    name: str
    children: list[Union['AssetClass', 'AssetClassCategory']]

    def __init__(self, name: str, children: list[Union['AssetClass', 'AssetClassCategory']]):
        self.name = name
        self.children = children

    @property
    def value(self):
        return sum(child.value for child in self.children)

    @property
    def target_weight(self):
        return sum(child.target_weight for child in self.children)

class AssetClass:
    """A group of holdings in a portfolio."""
    name: str
    target_weight: float
    children: list['Holding']

    def __init__(self, name: str, children: list['Holding'], target_weight: float):
        if not 0.0 <= target_weight <= 1.0:
            raise ValueError("target_weight must be between 0.0 and 1.0")
        self.name = name
        self.children = children
        self.target_weight = target_weight

    @property
    def value(self):
        return sum(child.value for child in self.children)

class Holding:
    """A holding in a portfolio which a ticker symbol and number of shares."""
    ticker: str
    shares: float
    _quote_service: QuoteService

    def __init__(self, ticker: str, shares: float, quote_service: QuoteService | None = None):
        self.ticker = ticker
        self.shares = shares
        self._quote_service = quote_service or YFinanceQuoteService()

    @property
    def name(self):
        return self.ticker

    @property
    def value(self):
        return self.shares * self._quote_service.get_price(self.ticker)
