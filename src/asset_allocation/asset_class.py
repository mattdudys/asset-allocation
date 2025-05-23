from abc import ABC, abstractmethod
from typing import Optional, Union, Any

from asset_allocation.transaction import Transaction
from .holding import Holding
from .visitor import Visitor


class AssetClass(ABC):
    """An asset class is a collection of holdings that are managed as a single entity.

    Asset classes can be nested to form a hierarchy of asset classes.
    """

    @property
    def name(self) -> str:
        """The name of this asset class."""
        return self._name

    @property
    def value(self) -> float:
        """The value of this asset class."""
        return sum(child.value for child in self.children)

    @property
    def children(self) -> list[Union["AssetClass", "Holding"]]:
        """The children of this asset class."""
        return self._children

    @property
    @abstractmethod
    def holdings(self) -> list[Holding]:
        """The holdings of this asset class."""
        pass

    @property
    @abstractmethod
    def target_weight(self) -> float:
        """The target weight of this asset class."""
        pass

    def actual_weight(self, investable_value: float) -> float:
        """The actual weight of this asset class in the portfolio."""
        if investable_value <= 0:
            raise ValueError("investable_value must be positive")
        return self.value / investable_value

    def fractional_deviation(self, investable_value: float) -> float:
        """How much this category deviates from its target weight.

        Args:
            investable_value: the investable, non-cash value of the portfolio

        Returns:
            The fractional deviation from target weight. Positive means overweight,
            negative means underweight. For example, 0.1 means 10% overweight,
            -0.1 means 10% underweight.
        """
        if investable_value <= 0:
            raise ValueError("investable_value must be positive")
        return (self.actual_weight(investable_value) / self.target_weight) - 1

    @property
    def rebalance_band(self) -> float:
        """How much overweight or underweight this asset class can be before we need to rebalance.

        We follow a 5/25 rule: consider rebalancing if the weight deviates by an absolute 5% or a relative 25%.

        Returns:
            A multiplier to apply to the target weight to get the rebalance band.
        """
        return min(0.05, self.target_weight * 0.25)

    @property
    def min_target_weight(self) -> float:
        """Calculate the lower bound of the desired weight.

        Returns:
            The lower bound of the desired weight
        """
        return self.target_weight - self.rebalance_band

    @property
    def max_target_weight(self) -> float:
        """Calculate the upper bound of the desired weight.

        Returns:
            The upper bound of the desired weight
        """
        return self.target_weight + self.rebalance_band

    def overweight(self, investable_value: float) -> bool:
        """Check if this asset class is overweight.

        Args:
            investable_value: the investable, non-cash value of the portfolio

        Returns:
            True if this asset class is overweight, False otherwise
        """
        return self.actual_weight(investable_value) > self.max_target_weight

    def underweight(self, investable_value: float) -> bool:
        """Check if this asset class is underweight.

        Args:
            total_portfolio_value: the investable, non-cash value of the portfolio

        Returns:
            True if this asset class is underweight, False otherwise
        """
        return self.actual_weight(investable_value) < self.min_target_weight

    @abstractmethod
    def buy(self, budget: float, investable_value: float) -> Optional[Transaction]:
        """Attempt to buy one share of a holding in this asset class."""
        pass

    @abstractmethod
    def sell(self, investable_value: float) -> Optional[Transaction]:
        """Attempt to sell one share of a holding in this asset class."""
        pass

    @abstractmethod
    def sell_overweight(self, investable_value: float) -> Optional[Transaction]:
        """Attempt to sell one share of an overweight holding in this asset class."""
        pass

    def visit(self, visitor: Visitor) -> None:
        """Visit this node with a visitor."""
        visitor.visit_asset_class(self)
        for child in self.children:
            child.visit(visitor)


class CompositeAssetClass(AssetClass):
    """A composite asset class that contains other asset classes."""

    _name: str
    _children: list[AssetClass]

    def __init__(self, name: str, children: list[AssetClass]):
        if not children:
            raise ValueError("CompositeAssetClass must have at least one child")
        self._name = name
        self._children = children

    @property
    def holdings(self) -> list[Holding]:
        return [holding for child in self.children for holding in child.holdings]

    @property
    def target_weight(self):
        return sum(child.target_weight for child in self.children)

    def buy(self, budget: float, investable_value: float) -> Optional[Transaction]:
        """Identifies the most underweight child asset class and attempts to buy one share of an underlying holding.

        Args:
            budget: the amount of money to spend
            investable_value: the investable, non-cash value of the portfolio
        Returns:
            A Transaction if there was enough budget, otherwise None
        """
        # Create a copy of the children list and sort it by fractional deviation ascending.
        children = sorted(
            self.children, key=lambda x: x.fractional_deviation(investable_value)
        )
        for child in children:
            transaction = child.buy(budget, investable_value)
            if transaction:
                return transaction
        return None

    def sell(self, investable_value: float) -> Optional[Transaction]:
        """Identifies the most overweight child asset class and attempts to sell one share of an underlying holding.

        Args:
            investable_value: the investable, non-cash value of the portfolio
        Returns:
            A Transaction if there was a share to sell, otherwise None
        """
        # Create a copy of the children list and sort it by fractional deviation descending.
        children = sorted(
            self.children,
            key=lambda x: x.fractional_deviation(investable_value),
            reverse=True,
        )
        for child in children:
            transaction = child.sell(investable_value)
            if transaction:
                return transaction
        return None

    def sell_overweight(self, investable_value: float) -> Optional[Transaction]:
        """Attempt to sell one share of the most overweight child asset class, only if it is overweight."""
        children = sorted(
            [child for child in self.children],
            key=lambda x: x.fractional_deviation(investable_value),
            reverse=True,
        )
        for child in children:
            transaction = child.sell_overweight(investable_value)
            if transaction:
                return transaction
        return None


class LeafAssetClass(AssetClass):
    """A leaf asset class is a group of holdings in a portfolio with a defined target weight.

    The children are Holdings and are in preference order:
    - When buying more of this asset class, we will buy more of the first Holding
    - When selling from this asset class, we will sell from the last Holding first,
      then the second-to-last, and so on
    """

    _name: str
    _target_weight: float
    _children: list[Holding]

    def __init__(self, name: str, target_weight: float, children: list[Holding]):
        if not 0.0 <= target_weight <= 1.0:
            raise ValueError("target_weight must be between 0.0 and 1.0")
        if not children:
            raise ValueError("AssetClass must have at least one holding")
        self._name = name
        self._target_weight = target_weight
        self._children = children

    @property
    def holdings(self) -> list[Holding]:
        return self._children

    @property
    def target_weight(self) -> float:
        return self._target_weight

    def buy(self, budget: float, investable_value: float) -> Optional[Transaction]:
        """Buy one share of this asset class's preferred holding if there is enough budget.

        Args:
            budget: the amount of money to spend
            investable_value: the investable, non-cash value of the portfolio

        Returns:
            A Transaction if there was enough budget, otherwise None
        """
        return self.children[0].buy(budget)

    def sell(self, investable_value: float) -> Optional[Transaction]:
        """Sell one share of this asset class's least preferred holding, or a fractional share if less than one share.

        Args:
            investable_value: the investable, non-cash value of the portfolio

        Returns:
            A Transaction if there was a share to sell, otherwise None
        """
        for child in reversed(self.children):
            transaction = child.sell()
            if transaction:
                return transaction
        return None

    def sell_overweight(self, investable_value: float) -> Optional[Transaction]:
        """Attempt to sell one share of this asset class if it is overweight."""
        if not self.overweight(investable_value):
            return None
        return self.sell(investable_value)
