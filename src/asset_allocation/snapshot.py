from dataclasses import dataclass
from typing import List

from .asset_class import AssetClass
from .holding import Holding
from .visitor import Visitor


@dataclass
class AssetClassSnapshot:
    """A snapshot of an AssetClassCategory or AssetClass node in the portfolio hierarchy."""

    name: str
    value: float
    target_weight: float
    actual_weight: float
    fractional_deviation: float
    underweight: bool
    overweight: bool


@dataclass
class HoldingSnapshot:
    """A snapshot of a Holding node in the portfolio hierarchy."""

    name: str
    value: float
    shares: float


@dataclass
class PortfolioSnapshot:
    """A snapshot of the entire portfolio."""

    cash: float
    value: float
    investible_value: float
    excess_cash: float
    asset_classes: List[AssetClassSnapshot]
    holdings: List[HoldingSnapshot]


class PortfolioSnapshotter(Visitor):
    """A visitor that creates a snapshot of the portfolio structure and values.

    The snapshot includes the name, value, target weight, and actual weight of each node,
    as well as its children in a hierarchical structure.
    """

    def __init__(self, portfolio: "Portfolio"):
        """Initialize the visitor.

        Args:
            portfolio: The portfolio to snapshot
        """
        self._portfolio = portfolio
        self.snapshot = PortfolioSnapshot(
            cash=portfolio.cash_value,
            value=portfolio.value,
            investible_value=portfolio.investible_value,
            excess_cash=portfolio.excess_cash,
            asset_classes=[],
            holdings=[],
        )

    def visit_asset_class(self, asset_class: AssetClass) -> None:
        """Record a snapshot of the AssetClass node.

        Args:
            asset_class: The AssetClass node being visited
        """
        self.snapshot.asset_classes.append(
            AssetClassSnapshot(
                name=asset_class.name,
                value=asset_class.value,
                target_weight=asset_class.target_weight,
                actual_weight=asset_class.actual_weight(
                    self._portfolio.investible_value
                ),
                fractional_deviation=asset_class.fractional_deviation(
                    self._portfolio.investible_value
                ),
                underweight=asset_class.underweight(self._portfolio.investible_value),
                overweight=asset_class.overweight(self._portfolio.investible_value),
            )
        )

    def visit_holding(self, holding: Holding) -> None:
        """Record a snapshot of the Holding node.

        Args:
            holding: The Holding node being visited
        """
        self.snapshot.holdings.append(
            HoldingSnapshot(
                name=holding.name,
                value=holding.value,
                shares=holding.shares,
            )
        )
