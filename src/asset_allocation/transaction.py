from dataclasses import dataclass
from typing import List

@dataclass
class Transaction:
    """A single buy or sell transaction."""
    ticker: str
    shares: float
    price: float
    transaction_type: str  # "BUY" or "SELL"

class TransactionLog:
    """A log of all buy and sell transactions in a portfolio."""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
    
    def log_buy(self, ticker: str, shares: float, price: float) -> None:
        """Log a buy transaction."""
        transaction = Transaction(
            ticker=ticker,
            shares=shares,
            price=price,
            transaction_type="BUY"
        )
        self.transactions.append(transaction)
    
    def log_sell(self, ticker: str, shares: float, price: float) -> None:
        """Log a sell transaction."""
        transaction = Transaction(
            ticker=ticker,
            shares=shares,
            price=price,
            transaction_type="SELL"
        )
        self.transactions.append(transaction) 