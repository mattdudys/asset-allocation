import yfinance
from .graph import LeafNode, InternalNode, Node

class Portfolio(InternalNode):
    """A portfolio of holdings."""
    cash_value: float
    cash_target: float | None

    def __init__(self, name: str, children: list[Node], cash_value: float = 0.0, cash_target: float | None = None):
        super().__init__(name, children)
        self.cash_value = cash_value
        self.cash_target = cash_target

class AssetClass(InternalNode):
    """A group of holdings or a group of asset classes in a portfolio."""
    target_allocation: float

    def __init__(self, name: str, children: list[Node], target_allocation: float):
        if not 0 <= target_allocation <= 100:
            raise ValueError("target_allocation must be between 0 and 100")
        super().__init__(name, children)
        self.target_allocation = target_allocation

class TickerHolding(LeafNode):
    """A holding in a portfolio which a ticker symbol and number of shares."""
    ticker: str
    shares: float
    _ticker: yfinance.Ticker

    def __init__(self, ticker: str, shares: float):
        self.ticker = ticker
        self.shares = shares
        self._ticker = yfinance.Ticker(ticker)

    @property
    def name(self):
        return self.ticker
    
    @property
    def value(self):
        return self.shares * self._ticker.info['regularMarketPrice'] 