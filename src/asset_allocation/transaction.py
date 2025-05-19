from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import pandas as pd


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


class Transactions:
    """A list of transactions produced by operations on a Portfolio."""

    _transactions: List[Transaction]

    def __init__(self, transactions: Optional[List[Transaction]] = None):
        if transactions is None:
            transactions = []
        self._transactions = transactions

    def __iter__(self):
        return iter(self._transactions)

    def __len__(self):
        return len(self._transactions)

    def __getitem__(self, index):
        return self._transactions[index]

    def append(self, transaction: Transaction):
        self._transactions.append(transaction)

    @property
    def empty(self):
        return len(self._transactions) == 0

    def buys(self) -> "Transactions":
        """Get all buy transactions."""
        return Transactions([t for t in self._transactions if t.type == BuySell.BUY])

    def sells(self) -> "Transactions":
        """Get all sell transactions."""
        return Transactions([t for t in self._transactions if t.type == BuySell.SELL])

    def ticker(self, ticker: str) -> "Transactions":
        """Get all transactions for a specific ticker."""
        return Transactions([t for t in self._transactions if t.ticker == ticker])

    @property
    def total_amount(self) -> float:
        """Calculate the total amount of all transactions."""
        return sum(t.amount for t in self._transactions)

    @property
    def total_shares(self) -> float:
        """Calculate the total shares of all transactions."""
        return sum(t.shares for t in self._transactions)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self._transactions)
