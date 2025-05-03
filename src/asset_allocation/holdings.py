from .quote_service import QuoteService, YFinanceQuoteService
from typing import Union

class Portfolio:
    """A portfolio of holdings."""
    cash_value: float
    cash_target: float | None

    def __init__(self, cash_value: float = 0.0, cash_target: float | None = None, children: list[Union['AssetClass', 'AssetClassCategory']] = None):
        self.children = children or []
        self.cash_value = cash_value
        self.cash_target = cash_target
        if self.children:  # Only validate if there are children
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

    def actual_weight(self, total_portfolio_value: float) -> float:
        """Calculate the actual weight of this category in the portfolio.
        
        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio
            
        Returns:
            The ratio of this category's value to the total portfolio value
        """
        if total_portfolio_value <= 0:
            raise ValueError("total_portfolio_value must be positive")
        return self.value / total_portfolio_value

    def fractional_deviation(self, total_portfolio_value: float) -> float:
        """Calculate how much this category deviates from its target weight.
        
        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio
            
        Returns:
            The fractional deviation from target weight. Positive means overweight,
            negative means underweight. For example, 0.1 means 10% overweight,
            -0.1 means 10% underweight.
        """
        if total_portfolio_value <= 0:
            raise ValueError("total_portfolio_value must be positive")
        return (self.actual_weight(total_portfolio_value) / self.target_weight) - 1

class AssetClass:
    """A group of holdings in a portfolio.
    
    The holdings are in preference order:
    - When buying more of this asset class, we will buy more of the first holding
    - When selling from this asset class, we will sell from the last holding first,
      then the second-to-last, and so on
    """
    name: str
    target_weight: float
    holdings: list['Holding']

    def __init__(self, name: str, target_weight: float, holdings: list['Holding']):
        if not 0.0 <= target_weight <= 1.0:
            raise ValueError("target_weight must be between 0.0 and 1.0")
        self.name = name
        self.target_weight = target_weight
        self.holdings = holdings

    @property
    def value(self):
        return sum(holding.value for holding in self.holdings)

    def actual_weight(self, total_portfolio_value: float) -> float:
        """Calculate the actual weight of this asset class in the portfolio.
        
        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio
            
        Returns:
            The ratio of this asset class's value to the total portfolio value
        """
        if total_portfolio_value <= 0:
            raise ValueError("total_portfolio_value must be positive")
        return self.value / total_portfolio_value

    def fractional_deviation(self, total_portfolio_value: float) -> float:
        """Calculate how much this asset class deviates from its target weight.
        
        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio
            
        Returns:
            The fractional deviation from target weight. Positive means overweight,
            negative means underweight. For example, 0.1 means 10% overweight,
            -0.1 means 10% underweight.
        """
        if total_portfolio_value <= 0:
            raise ValueError("total_portfolio_value must be positive")
        return (self.actual_weight(total_portfolio_value) / self.target_weight) - 1
    

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
        self.shares -= to_sell
        return to_sell * self.price
