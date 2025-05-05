from dataclasses import dataclass
from typing import List
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


class TransactionLog:
    """A log of all buy and sell transactions in a portfolio."""

    def __init__(self):
        self.transactions: List[Transaction] = []

    def __iter__(self):
        return iter(self.transactions)

    def append(self, transaction: Transaction):
        self.transactions.append(transaction)

    def empty(self):
        return len(self.transactions) == 0

    def to_dataframe(self):
        return pd.DataFrame(self.transactions)
