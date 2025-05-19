import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import CompositeAssetClass, LeafAssetClass
from asset_allocation.portfolio import Portfolio
from asset_allocation.transaction import BuySell


class TestPortfolio(unittest.TestCase):
    def test_empty_portfolio_creation(self):
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[])
        self.assertEqual(
            str(cm.exception),
            "Portfolio must have at least one asset class or category",
        )

    def test_portfolio_with_cash_target(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=0.2, children=[asset_class]
        )

        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 0.2)

    def test_portfolio_value_sums_children_and_cash(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(cash_value=1000.0, children=[asset_class])

        self.assertEqual(portfolio.value, 2000.0)  # 1000 (cash) + 1000 (holdings)

    def test_portfolio_rejects_invalid_target_weights(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=0.4, children=[holding])
        with self.assertRaises(ValueError) as cm:
            Portfolio(children=[asset_class])
        self.assertEqual(
            str(cm.exception), "Sum of target weights must be 1.0, got 0.4"
        )

    def test_portfolio_with_nested_categories(self):
        holding1 = Holding("VTI", 10, price=100.0)
        holding2 = Holding("VXUS", 10, price=100.0)
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )
        equity = CompositeAssetClass("Equity", [us_equity, intl_equity])

        holding3 = Holding("BND", 10, price=100.0)
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(cash_value=1000.0, children=[equity, fixed_income])

        self.assertEqual(portfolio.value, 4000.0)  # 1000 (cash) + 3000 (holdings)

    def test_excess_cash_calculation(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        self.assertEqual(portfolio.excess_cash, 500.0)  # 1000 - 500 target

    def test_excess_cash_with_no_target(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=None, children=[asset_class]
        )

        self.assertEqual(
            portfolio.excess_cash, 1000.0
        )  # All cash is excess when no target

    def test_excess_cash_below_target(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=300.0, cash_target=500.0, children=[asset_class]
        )

        self.assertEqual(portfolio.excess_cash, 0.0)  # No excess when below target

    def test_investible_value(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        # investible_value = investments (1000) + excess_cash (500)
        self.assertEqual(portfolio.investible_value, 1500.0)

    def test_invest_excess_cash(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        portfolio.invest_excess_cash()

        # After investing excess cash, cash should be at target
        self.assertEqual(portfolio.cash_value, 500.0)
        # Total value should remain the same (1000 cash + 1000 holdings)
        self.assertEqual(portfolio.value, 2000.0)
        # Holdings value should increase by the amount invested
        self.assertEqual(portfolio.investments.value, 1500.0)

    def test_invest_excess_cash_with_no_target(self):
        holding = Holding("VTI", 10, price=100.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=None, children=[asset_class]
        )

        portfolio.invest_excess_cash()

        # All cash should be invested when no target
        self.assertEqual(portfolio.cash_value, 0.0)
        # Total value should remain the same
        self.assertEqual(portfolio.value, 2000.0)

    def test_sell_overweight_with_overweight_asset(self):
        # Create a portfolio with an overweight asset
        # VTI value = 6000, which is 60% of investible value, but target is 40% (so it's 50% overweight)
        holding1 = Holding("VTI", 60, price=100.0)  # 6000
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])

        # VXUS value = 1000, which is 10% of investible value, but target is 20% (so it's 50% underweight)
        holding2 = Holding("VXUS", 10, price=100.0)  # 1000
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )

        # BND value = 3000, which is 30% of investible value, but target is 40% (so it's 25% underweight)
        holding3 = Holding("BND", 30, price=100.0)  # 3000
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(
            cash_value=0.0,  # No cash initially
            cash_target=0.0,  # No cash target
            children=[us_equity, intl_equity, fixed_income],
        )

        # Portfolio structure:
        # - US Equity (VTI): 6000 (60%) target 40% -> overweight
        # - International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # - Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)

        # Execute sell_overweight
        transaction_log = portfolio.sell_overweight()

        # Verify transactions occurred (exact count depends on implementation)
        self.assertFalse(transaction_log.empty)
        self.assertGreater(len(transaction_log.transactions), 0)

        # Verify all transactions are SELL type and only for VTI
        for transaction in transaction_log.transactions:
            self.assertEqual(transaction.type, BuySell.SELL)
            self.assertEqual(transaction.ticker, "VTI")

        # Calculate total shares sold
        total_shares_sold = sum(t.shares for t in transaction_log.transactions)

        # Verify portfolio state after selling
        self.assertEqual(holding1.shares, 60 - total_shares_sold)  # VTI reduced
        self.assertEqual(holding2.shares, 10)  # VXUS unchanged
        self.assertEqual(holding3.shares, 30)  # BND unchanged
        self.assertEqual(
            portfolio.cash_value, total_shares_sold * 100.0
        )  # Cash increased

        # Verify that VTI is no longer overweight or at least less overweight
        current_weight = holding1.value / portfolio.investible_value
        # Should be closer to target than original 60%
        self.assertLess(current_weight, 0.6)

    def test_sell_overweight_with_no_overweight_assets(self):
        # Create a balanced portfolio
        holding1 = Holding("VTI", 40, price=100.0)  # 4000 - exactly at target
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])

        holding2 = Holding("VXUS", 20, price=100.0)  # 2000 - exactly at target
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )

        holding3 = Holding("BND", 40, price=100.0)  # 4000 - exactly at target
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=0.0,
            children=[us_equity, intl_equity, fixed_income],
        )

        # Execute sell_overweight
        transaction_log = portfolio.sell_overweight()

        # Verify no transaction occurred
        self.assertTrue(transaction_log.empty)
        self.assertEqual(len(transaction_log.transactions), 0)

        # Verify portfolio state is unchanged
        self.assertEqual(holding1.shares, 40)
        self.assertEqual(holding2.shares, 20)
        self.assertEqual(holding3.shares, 40)
        self.assertEqual(portfolio.cash_value, 0.0)

    def test_rebalance_sells_all_overweight_followed_by_invest(self):
        """Test that sell_overweight sells all overweight assets and then invests the cash."""
        # Create overweight and underweight assets
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])

        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )

        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=0.0,
            children=[us_equity, intl_equity, fixed_income],
        )

        # First sell overweight assets
        transaction_log = portfolio.sell_overweight()

        # Verify sell transactions occurred (exact count depends on implementation)
        self.assertFalse(transaction_log.empty)
        self.assertGreater(len(transaction_log.transactions), 0)

        # Verify all transactions are SELL type and for VTI
        for transaction in transaction_log.transactions:
            self.assertEqual(transaction.type, BuySell.SELL)
            self.assertEqual(transaction.ticker, "VTI")

        # Calculate total cash generated from selling
        total_cash_from_selling = portfolio.cash_value
        self.assertGreater(total_cash_from_selling, 0)

        # Save the number of transactions before investing
        num_transactions_before_invest = len(transaction_log.transactions)

        # Now invest the excess cash from selling
        transaction_log = portfolio.invest_excess_cash(transaction_log)

        # Verify buy transactions occurred
        self.assertGreater(
            len(transaction_log.transactions), num_transactions_before_invest
        )

        # Verify the new transactions are BUY type
        for i in range(
            num_transactions_before_invest, len(transaction_log.transactions)
        ):
            self.assertEqual(transaction_log.transactions[i].type, BuySell.BUY)

        # Cash should be close to 0 (or exactly 0 if everything could be invested)
        self.assertLess(portfolio.cash_value, total_cash_from_selling)

        # Verify either VXUS or BND (or both) increased in shares
        self.assertTrue(
            holding2.shares > 10 or holding3.shares > 30,
            "Either VXUS or BND should have increased in shares",
        )

    def test_divest_sells_until_cash_target(self):
        """Test that divest sells overweight assets until cash target is met."""
        # Create overweight and underweight assets
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])

        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )

        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=200.0,  # Set a cash target
            children=[us_equity, intl_equity, fixed_income],
        )

        # Portfolio structure:
        # - US Equity (VTI): 6000 (60%) target 40% -> overweight
        # - International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # - Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)

        # Execute divest
        transaction_log = portfolio.divest()

        # Verify sell transactions occurred and stopped when cash target was met
        self.assertFalse(transaction_log.empty)
        # We expect to sell 2 shares of VTI to reach the 200 cash target
        self.assertEqual(
            len([t for t in transaction_log.transactions if t.type == BuySell.SELL]), 2
        )
        self.assertEqual(portfolio.cash_value, 200.0)

        # Verify all sell transactions are SELL type and only for VTI
        for transaction in [
            t for t in transaction_log.transactions if t.type == BuySell.SELL
        ]:
            self.assertEqual(transaction.type, BuySell.SELL)
            self.assertEqual(transaction.ticker, "VTI")

        # Verify no buy transactions occurred
        buy_transactions = [
            t for t in transaction_log.transactions if t.type == BuySell.BUY
        ]
        self.assertEqual(len(buy_transactions), 0)

        # Verify shares of underweight assets did not change
        self.assertEqual(holding2.shares, 10)
        self.assertEqual(holding3.shares, 30)

    def test_divest_sells_all_overweight_when_cash_target_high(self):
        """Test that divest sells all overweight assets when cash target is higher than total value."""
        # Create overweight and underweight assets
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        us_equity = LeafAssetClass("US Equity", target_weight=0.4, children=[holding1])

        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        intl_equity = LeafAssetClass(
            "International Equity", target_weight=0.2, children=[holding2]
        )

        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight
        fixed_income = LeafAssetClass(
            "Fixed Income", target_weight=0.4, children=[holding3]
        )

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=15000.0,  # Set a cash target higher than total value
            children=[us_equity, intl_equity, fixed_income],
        )

        # Portfolio structure:
        # - US Equity (VTI): 6000 (60%) target 40% -> overweight
        # - International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # - Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)

        # Execute divest
        transaction_log = portfolio.divest()

        # All investments should be sold and cash should be 10000.
        self.assertEqual(portfolio.investments.value, 0.0)
        self.assertEqual(portfolio.cash_value, 10000.0)

        # Verify all transactions are SELL and total sold is 10000.
        self.assertFalse(transaction_log.empty)
        self.assertEqual(
            sum(
                t.amount for t in transaction_log.transactions if t.type == BuySell.SELL
            ),
            10000.0,
        )


if __name__ == "__main__":
    unittest.main()
