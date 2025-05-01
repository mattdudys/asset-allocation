import yfinance
from typing import Optional

# asset_allocation represents a portfolio of stocks or ETFs categorized into a hierarchy of groups.

class Graph:
    def __init__(self):
        self.nodes = {}

class Node:
    name: str
    parent: Optional['Node']
    value: float

    def __init__(self, name: str, parent: Optional['Node'] = None):
        self.name = name
        self.parent = parent

class LeafNode(Node):
    @property
    def children(self):
        return []

class InternalNode(Node):
    children: list[Node]

    def __init__(self, name: str, children: list[Node]):
        super().__init__(name)
        self.children = children

    @property
    def value(self):
        return sum(child.value for child in self.children)
    
class HoldingGroup(InternalNode):
    """A group of holdings or a group of groups in a portfolio. These may be asset classes, sectors, or regions."""
    def __init__(self, name: str, children: list[Node]):
        super().__init__(name, children)

    
class CashHolding(LeafNode):
    """The cash holding in the portfolio."""

    def __init__(self, value: float):
        self.name = "Cash"
        self.value = value
        

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
