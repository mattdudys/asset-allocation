from typing import Union
from .asset_class import AssetClass, AssetClassCategory

class Portfolio:
    """A portfolio of holdings."""
    cash_value: float
    cash_target: float | None
    investments: AssetClassCategory

    def __init__(self, cash_value: float = 0.0, cash_target: float | None = None, children: list[Union[AssetClass, AssetClassCategory]] = None):
        self.cash_value = cash_value
        self.cash_target = cash_target
        if not children:
            raise ValueError("Portfolio must have at least one asset class or category")
        self.investments = AssetClassCategory("Total", children)
        self._validate_target_weights()

    def _validate_target_weights(self):
        """Validate that the sum of target weights is 1.0."""
        if not abs(self.investments.target_weight - 1.0) < 0.001:  # Using small epsilon for float comparison
            raise ValueError(f"Sum of target weights must be 1.0, got {self.investments.target_weight}")

    @property
    def value(self):
        return self.investments.value + self.cash_value 