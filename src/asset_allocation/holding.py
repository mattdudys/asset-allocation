from typing import Optional
from asset_allocation.transaction import BuySell, Transaction
from .quote_service import QuoteService

class Holding:
    """A holding in a portfolio which a ticker symbol and number of shares."""
    ticker: str
    shares: float
    price: float

    def __init__(self, ticker: str, shares: float, price: float):
        self.ticker = ticker
        self.shares = shares
        self.price = price
        if price <= 0:
            raise ValueError("price must be positive")

    @classmethod
    def from_quote_service(cls, ticker: str, shares: float, quote_service: QuoteService) -> 'Holding':
        """Create a holding with a live price from a quote service.
        
        Args:
            ticker: the ticker symbol
            shares: the number of shares
            quote_service: the service to get the current price
            
        Returns:
            A new Holding instance with the current price
        """
        price = quote_service.get_price(ticker)
        return cls(ticker, shares, price)

    @property
    def name(self):
        return self.ticker

    @property
    def value(self):
        return self.shares * self.price

    def buy(self, budget: float) -> Optional[Transaction]:
        """Buy one share of this holding if there is enough budget.
        
        Args:
            budget: the amount of money to spend
        Returns: 
            A Transaction if there was enough budget, otherwise None
        """
        if budget < self.price:
            return None
        self.shares += 1
        return Transaction(
            type=BuySell.BUY,
            ticker=self.ticker,
            shares=1,
            price=self.price,
            amount=self.price,
        )
    
    def sell(self) -> Optional[Transaction]:
        """Sell one share of this holding, or a fractional share if less than one share.
        
        Returns:
            A Transaction if there was a share to sell, otherwise None
        """
        to_sell = min(self.shares, 1.0)
        if to_sell <= 0:
            return None
        self.shares -= to_sell
        return Transaction(
            type=BuySell.SELL,
            ticker=self.ticker,
            shares=to_sell,
            price=self.price,
            amount=to_sell * self.price,
        )
