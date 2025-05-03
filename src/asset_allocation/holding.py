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

    def buy(self, budget: float) -> float:
        """Buy one share of this holding if there is enough budget.
        
        Args:
            budget: the amount of money to spend
        Returns: 
            The amount of money spent or 0 if there is not enough budget
        """
        if budget < self.price:
            return 0
        self.shares += 1
        return self.price
    
    def sell(self) -> float:
        """Sell one share of this holding, or a fractional share if less than one share.
        
        Returns:
            The proceeds of the sale, if any.
        """
        to_sell = min(self.shares, 1.0)
        if to_sell <= 0:
            return 0
        self.shares -= to_sell
        return to_sell * self.price 