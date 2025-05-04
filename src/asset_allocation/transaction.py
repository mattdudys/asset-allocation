from dataclasses import dataclass
from typing import List
from enum import Enum


class BuySell(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Transaction:
    """A single buy or sell transaction."""

    type: BuySell
    ticker: str
    shares: float
    price: float
    amount: float


class TransactionLog:
    """A log of all buy and sell transactions in a portfolio."""

    def __init__(self):
        self.transactions: List[Transaction] = []

    def log_buy(self, ticker: str, shares: float, price: float) -> None:
        """Log a buy transaction."""
        transaction = Transaction(
            type=BuySell.BUY,
            ticker=ticker,
            shares=shares,
            price=price,
            amount=shares * price,
        )
        self.transactions.append(transaction)

    def log_sell(self, ticker: str, shares: float, price: float) -> None:
        """Log a sell transaction."""
        transaction = Transaction(
            type=BuySell.SELL,
            ticker=ticker,
            shares=shares,
            price=price,
            amount=shares * price,
        )
        self.transactions.append(transaction)
