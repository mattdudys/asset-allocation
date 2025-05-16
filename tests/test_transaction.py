import unittest
import pandas as pd
from asset_allocation.transaction import Transaction, TransactionLog, BuySell


class TestTransaction(unittest.TestCase):
    """Tests for the Transaction class."""

    def test_transaction_creation_buy(self):
        """Test creation of a buy transaction with proper attributes."""
        transaction = Transaction(
            type=BuySell.BUY, ticker="VOO", shares=5, price=400.0, amount=2000.0
        )

        self.assertEqual(transaction.type, BuySell.BUY)
        self.assertEqual(transaction.ticker, "VOO")
        self.assertEqual(transaction.shares, 5)
        self.assertEqual(transaction.price, 400.0)
        self.assertEqual(transaction.amount, 2000.0)

    def test_transaction_creation_sell(self):
        """Test creation of a sell transaction with proper attributes."""
        transaction = Transaction(
            type=BuySell.SELL, ticker="VIOV", shares=10, price=150.0, amount=1500.0
        )

        self.assertEqual(transaction.type, BuySell.SELL)
        self.assertEqual(transaction.ticker, "VIOV")
        self.assertEqual(transaction.shares, 10)
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.amount, 1500.0)

    def test_transaction_fractional_shares(self):
        """Test that transactions support fractional shares."""
        transaction = Transaction(
            type=BuySell.SELL, ticker="VTEB", shares=0.5, price=50.0, amount=25.0
        )

        self.assertEqual(transaction.shares, 0.5)
        self.assertEqual(transaction.amount, 25.0)


class TestTransactionLog(unittest.TestCase):
    """Tests for the TransactionLog class."""

    def test_empty_transaction_log(self):
        """Test that a new transaction log is empty."""
        log = TransactionLog()
        self.assertTrue(log.empty)
        self.assertEqual(len(log.transactions), 0)

    def test_append_transaction(self):
        """Test adding a transaction to the log."""
        log = TransactionLog()
        transaction = Transaction(
            type=BuySell.BUY, ticker="VOO", shares=5, price=400.0, amount=2000.0
        )

        log.append(transaction)

        self.assertFalse(log.empty)
        self.assertEqual(len(log.transactions), 1)
        self.assertEqual(log.transactions[0], transaction)

    def test_append_multiple_transactions(self):
        """Test adding multiple transactions to the log."""
        log = TransactionLog()

        transaction1 = Transaction(
            type=BuySell.BUY, ticker="VOO", shares=5, price=400.0, amount=2000.0
        )

        transaction2 = Transaction(
            type=BuySell.SELL, ticker="VIOV", shares=10, price=150.0, amount=1500.0
        )

        log.append(transaction1)
        log.append(transaction2)

        self.assertEqual(len(log.transactions), 2)
        self.assertEqual(log.transactions[0], transaction1)
        self.assertEqual(log.transactions[1], transaction2)

    def test_transaction_log_iteration(self):
        """Test that TransactionLog supports iteration."""
        log = TransactionLog()

        transactions = [
            Transaction(
                type=BuySell.BUY, ticker="VOO", shares=5, price=400.0, amount=2000.0
            ),
            Transaction(
                type=BuySell.SELL, ticker="VIOV", shares=10, price=150.0, amount=1500.0
            ),
        ]

        for transaction in transactions:
            log.append(transaction)

        # Test iteration through the log
        for i, transaction in enumerate(log):
            self.assertEqual(transaction, transactions[i])

    def test_to_dataframe(self):
        """Test converting a TransactionLog to a pandas DataFrame."""
        log = TransactionLog()

        transactions = [
            Transaction(
                type=BuySell.BUY, ticker="VOO", shares=5, price=400.0, amount=2000.0
            ),
            Transaction(
                type=BuySell.SELL, ticker="VIOV", shares=10, price=150.0, amount=1500.0
            ),
        ]

        for transaction in transactions:
            log.append(transaction)

        df = log.to_dataframe()

        # Verify DataFrame structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertTrue(
            all(
                col in df.columns
                for col in ["type", "ticker", "shares", "price", "amount"]
            )
        )

        # Verify values
        self.assertEqual(df.iloc[0]["ticker"], "VOO")
        self.assertEqual(df.iloc[0]["shares"], 5)
        self.assertEqual(df.iloc[1]["ticker"], "VIOV")
        self.assertEqual(df.iloc[1]["amount"], 1500.0)

    def test_empty_to_dataframe(self):
        """Test converting an empty TransactionLog to a DataFrame."""
        log = TransactionLog()
        df = log.to_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)


if __name__ == "__main__":
    unittest.main()
