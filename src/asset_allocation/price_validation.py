"""Price validation and warning system for quote services."""

import warnings
from typing import Optional

# Constants for validation
MAX_SPREAD_PERCENTAGE = 0.05  # 5% maximum spread


def validate_prices(
    ticker: str,
    market_price: float,
    bid_price: Optional[float] = None,
    ask_price: Optional[float] = None,
) -> None:
    """Validate prices and issue warnings for any anomalies.

    Args:
        ticker: The ticker symbol being validated
        market_price: The current market price
        bid_price: Optional bid price to validate
        ask_price: Optional ask price to validate

    Issues warnings for:
    - bid > ask price
    - bid > market price
    - ask < market price
    - spread > 5% of market price
    """
    if bid_price is not None and ask_price is not None:
        if bid_price > ask_price:
            warnings.warn(
                f"Bid price ({bid_price:.2f}) is higher than ask price ({ask_price:.2f}) for {ticker}"
            )

        spread = abs(ask_price - bid_price)
        spread_percentage = spread / market_price
        if spread_percentage > MAX_SPREAD_PERCENTAGE:
            warnings.warn(
                f"Large spread detected for {ticker}: {spread_percentage:.1%} "
                f"(bid: {bid_price:.2f}, ask: {ask_price:.2f}, market: {market_price:.2f})"
            )

    if bid_price is not None and bid_price > market_price:
        warnings.warn(
            f"Bid price ({bid_price:.2f}) is higher than market price ({market_price:.2f}) for {ticker}"
        )

    if ask_price is not None and ask_price < market_price:
        warnings.warn(
            f"Ask price ({ask_price:.2f}) is lower than market price ({market_price:.2f}) for {ticker}"
        )
