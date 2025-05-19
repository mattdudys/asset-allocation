import unittest
import pandas as pd
from asset_allocation.transaction import Transaction, Transactions, BuySell


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


class TestTransactions(unittest.TestCase):
    """Tests for the Transactions class."""

    def test_empty_transactions(self):
        transactions = Transactions()
        self.assertTrue(transactions.empty)
        self.assertEqual(len(transactions), 0)

    def test_append_transaction(self):
        transactions = Transactions()
        transaction = Transaction(
            type=BuySell.BUY, ticker="VTI", shares=2, price=200.0, amount=400.0
        )

        transactions.append(transaction)

        self.assertFalse(transactions.empty)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], transaction)

    def test_iteration_and_indexing(self):
        t1 = Transaction(BuySell.BUY, "VTI", 2, 200.0, 400.0)
        t2 = Transaction(BuySell.SELL, "VXUS", 3, 100.0, 300.0)
        transactions = Transactions([t1, t2])

        transaction_list = list(transactions)
        self.assertEqual(len(transaction_list), 2)
        self.assertEqual(transaction_list[0], t1)
        self.assertEqual(transaction_list[1], t2)

        self.assertEqual(transactions[0], t1)
        self.assertEqual(transactions[1], t2)

    def test_filter_by_type(self):
        transactions = Transactions(
            [
                Transaction(BuySell.BUY, "VTI", 2, 200.0, 400.0),
                Transaction(BuySell.SELL, "VXUS", 3, 100.0, 300.0),
                Transaction(BuySell.BUY, "BND", 5, 80.0, 400.0),
            ]
        )

        buys = transactions.buys()
        sells = transactions.sells()

        self.assertEqual(len(buys), 2)
        self.assertEqual(len(sells), 1)
        self.assertTrue(all(t.type == BuySell.BUY for t in buys))
        self.assertTrue(all(t.type == BuySell.SELL for t in sells))

    def test_filter_by_ticker(self):
        transactions = Transactions(
            [
                Transaction(BuySell.BUY, "VTI", 2, 200.0, 400.0),
                Transaction(BuySell.SELL, "VTI", 1, 210.0, 210.0),
                Transaction(BuySell.BUY, "BND", 5, 80.0, 400.0),
            ]
        )

        vti_transactions = transactions.ticker("VTI")
        bnd_transactions = transactions.ticker("BND")

        self.assertEqual(len(vti_transactions), 2)
        self.assertEqual(len(bnd_transactions), 1)
        self.assertTrue(all(t.ticker == "VTI" for t in vti_transactions))
        self.assertTrue(all(t.ticker == "BND" for t in bnd_transactions))

    def test_total_calculations(self):
        transactions = Transactions(
            [
                Transaction(BuySell.BUY, "VTI", 2, 200.0, 400.0),
                Transaction(BuySell.BUY, "VXUS", 3, 100.0, 300.0),
                Transaction(BuySell.SELL, "VTI", 1, 210.0, 210.0),
            ]
        )

        self.assertEqual(transactions.total_amount, 910.0)
        self.assertEqual(transactions.total_shares, 6.0)

    def test_to_dataframe_conversion(self):
        transactions = Transactions(
            [
                Transaction(BuySell.BUY, "VTI", 2, 200.0, 400.0),
                Transaction(BuySell.SELL, "VXUS", 3, 100.0, 300.0),
            ]
        )

        df = transactions.to_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertTrue(
            all(
                col in df.columns
                for col in ["type", "ticker", "shares", "price", "amount"]
            )
        )
