from typing import Union
from .holding import Holding

class AssetClassCategory:
    """A category that can contain other asset classes or categories."""
    name: str
    children: list[Union['AssetClass', 'AssetClassCategory']]

    def __init__(self, name: str, children: list[Union['AssetClass', 'AssetClassCategory']]):
        if not children:
            raise ValueError("AssetClassCategory must have at least one child")
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

    def buy(self, budget: float, total_portfolio_value: float) -> float:
        """Identifies the most underweight child asset class and attempts to buy one share of an underlying holding.

        Args:
            budget: the amount of money to spend
            total_portfolio_value: the investable, non-cash value of the portfolio
        Returns:
            The amount of money spent or 0 if there is not enough budget
        """
        # Create a copy of the children list and sort it by fractional deviation ascending.
        children = sorted(self.children, key=lambda x: x.fractional_deviation(total_portfolio_value))
        for child in children:
            spent = child.buy(budget, total_portfolio_value)
            if spent > 0:
                return spent
        return 0
    
    def sell(self, total_portfolio_value: float) -> float:
        """Identifies the most overweight child asset class and attempts to sell one share of an underlying holding.

        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio
        Returns:
            The amount of money received or 0 if there is nothing to sell
        """
        # Create a copy of the children list and sort it by fractional deviation descending.
        children = sorted(self.children, key=lambda x: x.fractional_deviation(total_portfolio_value), reverse=True)
        for child in children:
            proceeds = child.sell()
            if proceeds > 0:
                return proceeds
        return 0

class AssetClass:
    """A group of holdings in a portfolio.
    
    The holdings are in preference order:
    - When buying more of this asset class, we will buy more of the first holding
    - When selling from this asset class, we will sell from the last holding first,
      then the second-to-last, and so on
    """
    name: str
    target_weight: float
    holdings: list[Holding]

    def __init__(self, name: str, target_weight: float, holdings: list[Holding]):
        if not 0.0 <= target_weight <= 1.0:
            raise ValueError("target_weight must be between 0.0 and 1.0")
        if not holdings:
            raise ValueError("AssetClass must have at least one holding")
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

    def buy(self, budget: float, total_portfolio_value: float) -> float:
        """Buy one share of this asset class's preferred holding if there is enough budget.
        
        Args:
            budget: the amount of money to spend
            total_portfolio_value: the investable, non-cash value of the portfolio
            
        Returns:
            The amount of money spent or 0 if there is not enough budget
        """
        return self.holdings[0].buy(budget)

    def sell(self) -> float:
        """Sell one share of this asset class's least preferred holding, or a fractional share if less than one share.
        
        Returns:
            The proceeds of the sale, if any.
        """
        for holding in reversed(self.holdings):
            proceeds = holding.sell()
            if proceeds > 0:
                return proceeds
        return 0 