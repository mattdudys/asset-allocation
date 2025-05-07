from typing import Union, List

from asset_allocation.transaction import TransactionLog
from .asset_class import AssetClass, CompositeAssetClass
from .snapshot import PortfolioSnapshot, PortfolioSnapshotter


class Portfolio:
    """A portfolio of holdings."""

    cash_value: float
    cash_target: float
    investments: AssetClass

    def __init__(
        self,
        cash_value: float = 0.0,
        cash_target: float = 0.0,
        children: List[AssetClass] = None,
    ):
        self.cash_value = cash_value
        self.cash_target = cash_target
        if not children:
            raise ValueError("Portfolio must have at least one asset class or category")
        self.investments = CompositeAssetClass("Total", children)
        self._validate_target_weights()

    def _validate_target_weights(self):
        """Validate that the sum of target weights is 1.0."""
        if (
            not abs(self.investments.target_weight - 1.0) < 0.001
        ):  # Using small epsilon for float comparison
            raise ValueError(
                f"Sum of target weights must be 1.0, got {self.investments.target_weight}"
            )

    @property
    def value(self):
        return self.investments.value + self.cash_value

    @property
    def excess_cash(self):
        """The amount of cash that is above the cash target."""
        if self.cash_target is None:
            return self.cash_value  # All cash is excess when no target
        return max(0, self.cash_value - self.cash_target)

    @property
    def investible_value(self):
        """The value of the portfolio's investments and excess cash."""
        return self.investments.value + self.excess_cash

    def invest_excess_cash(self) -> TransactionLog:
        """While there is excess cash, invest it in the portfolio."""
        transactions = TransactionLog()
        while self.excess_cash > 0:
            transaction = self.investments.buy(self.excess_cash, self.investible_value)
            if transaction:
                self.cash_value -= transaction.amount
                transactions.append(transaction)
            else:
                break
        return transactions

    def snapshot(self) -> PortfolioSnapshot:
        """Create a snapshot of the portfolio structure and values.

        Returns:
            A PortfolioSnapshot containing the portfolio's data and its hierarchical structure
        """
        visitor = PortfolioSnapshotter(self)
        self.investments.visit(visitor)
        return visitor.snapshot
