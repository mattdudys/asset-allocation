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
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=0.2,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        self.assertEqual(portfolio.cash_value, 1000.0)
        self.assertEqual(portfolio.cash_target, 0.2)

    def test_portfolio_value_sums_children_and_cash(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        self.assertEqual(portfolio.value, 2000.0)  # 1000 (cash) + 1000 (holdings)

    def test_portfolio_rejects_invalid_target_weights(self):
        with self.assertRaises(ValueError) as cm:
            Portfolio(
                children=[
                    LeafAssetClass(
                        "US Equity",
                        target_weight=0.4,
                        children=[Holding("VTI", 10, price=100.0)],
                    )
                ]
            )
        self.assertEqual(
            str(cm.exception), "Sum of target weights must be 1.0, got 0.4"
        )

    def test_portfolio_with_nested_categories(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            children=[
                CompositeAssetClass(
                    "Equity",
                    [
                        LeafAssetClass(
                            "US Equity",
                            target_weight=0.4,
                            children=[Holding("VTI", 10, price=100.0)],
                        ),
                        LeafAssetClass(
                            "International Equity",
                            target_weight=0.2,
                            children=[Holding("VXUS", 10, price=100.0)],
                        ),
                    ],
                ),
                LeafAssetClass(
                    "Fixed Income",
                    target_weight=0.4,
                    children=[Holding("BND", 10, price=100.0)],
                ),
            ],
        )

        self.assertEqual(portfolio.value, 4000.0)  # 1000 (cash) + 3000 (holdings)

    def test_excess_cash_calculation(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=500.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        self.assertEqual(portfolio.excess_cash, 500.0)  # 1000 - 500 target

    def test_excess_cash_with_no_target(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=None,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        self.assertEqual(
            portfolio.excess_cash, 1000.0
        )  # All cash is excess when no target

    def test_excess_cash_below_target(self):
        portfolio = Portfolio(
            cash_value=300.0,
            cash_target=500.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        self.assertEqual(portfolio.excess_cash, 0.0)  # No excess when below target

    def test_investible_value(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=500.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        # investible_value = investments (1000) + excess_cash (500)
        self.assertEqual(portfolio.investible_value, 1500.0)

    def test_invest_excess_cash(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=500.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        portfolio.invest_excess_cash()

        # After investing excess cash, cash should be at target
        self.assertEqual(portfolio.cash_value, 500.0)
        # Total value should remain the same (1000 cash + 1000 holdings)
        self.assertEqual(portfolio.value, 2000.0)
        # Holdings value should increase by the amount invested
        self.assertEqual(portfolio.investments.value, 1500.0)

    def test_invest_excess_cash_with_no_target(self):
        portfolio = Portfolio(
            cash_value=1000.0,
            cash_target=None,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=1.0,
                    children=[Holding("VTI", 10, price=100.0)],
                )
            ],
        )

        portfolio.invest_excess_cash()

        # All cash should be invested when no target
        self.assertEqual(portfolio.cash_value, 0.0)
        # Total value should remain the same
        self.assertEqual(portfolio.value, 2000.0)

    def test_sell_overweight_with_overweight_asset(self):
        # US Equity (VTI): 6000 (60%) target 40% -> overweight
        # International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)
        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=0.0,
            children=[
                CompositeAssetClass(
                    "Equity",
                    children=[
                        LeafAssetClass(
                            "US Equity",
                            target_weight=0.4,
                            children=[Holding("VTI", 60, price=100.0)],
                        ),
                        LeafAssetClass(
                            "International Equity",
                            target_weight=0.2,
                            children=[Holding("VXUS", 10, price=100.0)],
                        ),
                    ],
                ),
                LeafAssetClass(
                    "Fixed Income",
                    target_weight=0.4,
                    children=[Holding("BND", 30, price=100.0)],
                ),
            ],
        )

        # Execute sell_overweight
        transactions = portfolio.sell_overweight()

        # Verify transactions occurred (exact count depends on implementation)
        self.assertFalse(transactions.empty)

        # Verify all transactions are SELL type and only for VTI
        self.assertEqual(len(transactions), len(transactions.sells().ticker("VTI")))

        # Verify portfolio state after selling
        self.assertEqual(
            portfolio.holding("VTI").shares, 60 - transactions.total_shares
        )  # VTI reduced
        self.assertEqual(portfolio.holding("VXUS").shares, 10)  # VXUS unchanged
        self.assertEqual(portfolio.holding("BND").shares, 30)  # BND unchanged
        self.assertEqual(
            portfolio.cash_value, transactions.total_amount
        )  # Cash increased

        # Verify that VTI is no longer overweight or at least less overweight
        current_weight = portfolio.holding("VTI").value / portfolio.investible_value
        # Should be closer to target than original 60%
        self.assertLess(current_weight, 0.6)

    def test_sell_overweight_with_no_overweight_assets(self):
        # Create a balanced portfolio
        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=0.0,
            children=[
                LeafAssetClass(
                    "US Equity",
                    target_weight=0.4,
                    children=[Holding("VTI", 40, price=100.0)],
                ),  # 4000 - exactly at target
                LeafAssetClass(
                    "International Equity",
                    target_weight=0.2,
                    children=[Holding("VXUS", 20, price=100.0)],
                ),  # 2000 - exactly at target
                LeafAssetClass(
                    "Fixed Income",
                    target_weight=0.4,
                    children=[Holding("BND", 40, price=100.0)],
                ),  # 4000 - exactly at target
            ],
        )

        # Execute sell_overweight
        transactions = portfolio.sell_overweight()

        # Verify no transaction occurred
        self.assertTrue(transactions.empty)

        # Verify portfolio state is unchanged
        self.assertEqual(portfolio.holding("VTI").shares, 40)
        self.assertEqual(portfolio.holding("VXUS").shares, 20)
        self.assertEqual(portfolio.holding("BND").shares, 40)
        self.assertEqual(portfolio.cash_value, 0.0)

    def test_rebalance_sells_all_overweight_followed_by_invest(self):
        """Test that sell_overweight sells all overweight assets and then invests the cash."""
        # Create overweight and underweight assets for assertions
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=0.0,
            children=[
                LeafAssetClass("US Equity", target_weight=0.4, children=[holding1]),
                LeafAssetClass(
                    "International Equity", target_weight=0.2, children=[holding2]
                ),
                LeafAssetClass("Fixed Income", target_weight=0.4, children=[holding3]),
            ],
        )

        # First sell overweight assets
        sell_overweight_transactions = portfolio.sell_overweight()

        # Verify sell transactions occurred (exact count depends on implementation)
        self.assertFalse(sell_overweight_transactions.empty)

        # Verify all transactions are SELL type and for VTI
        self.assertEqual(
            len(sell_overweight_transactions),
            len(sell_overweight_transactions.sells().ticker("VTI")),
        )

        # Calculate total cash generated from selling
        self.assertGreater(portfolio.cash_value, 0)

        # Now invest the excess cash from selling
        invest_transactions = portfolio.invest_excess_cash()

        # Verify buy transactions occurred
        self.assertFalse(invest_transactions.empty)

        # Verify the new transactions are BUY type
        self.assertEqual(
            len(invest_transactions),
            len(invest_transactions.buys()),
        )

        # Cash should be close to 0 (or exactly 0 if everything could be invested)
        self.assertLess(portfolio.cash_value, sell_overweight_transactions.total_amount)

        # Verify either VXUS or BND (or both) increased in shares
        self.assertGreater(portfolio.holding("VXUS").shares, 10)

        self.assertTrue(
            holding2.shares > 10 or holding3.shares > 30,
            "Either VXUS or BND should have increased in shares",
        )

    def test_divest_sells_until_cash_target(self):
        """Test that divest sells overweight assets until cash target is met."""
        # Create holdings for assertions
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=200.0,  # Set a cash target
            children=[
                LeafAssetClass("US Equity", target_weight=0.4, children=[holding1]),
                LeafAssetClass(
                    "International Equity", target_weight=0.2, children=[holding2]
                ),
                LeafAssetClass("Fixed Income", target_weight=0.4, children=[holding3]),
            ],
        )

        # Portfolio structure:
        # - US Equity (VTI): 6000 (60%) target 40% -> overweight
        # - International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # - Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)

        # Execute divest
        transactions = portfolio.divest()

        # Verify sell transactions occurred and stopped when cash target was met
        self.assertFalse(transactions.empty)
        # We expect to sell 2 shares of VTI to reach the 200 cash target
        self.assertEqual(transactions.sells().ticker("VTI").total_shares, 2)
        self.assertEqual(portfolio.cash_value, 200.0)

        # Verify all sell transactions are SELL type and only for VTI
        self.assertEqual(len(transactions), len(transactions.sells().ticker("VTI")))

        # Verify no buy transactions occurred
        self.assertTrue(transactions.buys().empty)

        # Verify shares of underweight assets did not change
        self.assertEqual(holding2.shares, 10)
        self.assertEqual(holding3.shares, 30)

    def test_divest_sells_all_overweight_when_cash_target_high(self):
        """Test that divest sells all overweight assets when cash target is higher than total value."""
        # Create holdings for assertions
        holding1 = Holding("VTI", 60, price=100.0)  # 6000 - overweight
        holding2 = Holding("VXUS", 10, price=100.0)  # 1000 - underweight
        holding3 = Holding("BND", 30, price=100.0)  # 3000 - underweight

        portfolio = Portfolio(
            cash_value=0.0,
            cash_target=15000.0,  # Set a cash target higher than total value
            children=[
                LeafAssetClass("US Equity", target_weight=0.4, children=[holding1]),
                LeafAssetClass(
                    "International Equity", target_weight=0.2, children=[holding2]
                ),
                LeafAssetClass("Fixed Income", target_weight=0.4, children=[holding3]),
            ],
        )

        # Portfolio structure:
        # - US Equity (VTI): 6000 (60%) target 40% -> overweight
        # - International Equity (VXUS): 1000 (10%) target 20% -> underweight
        # - Fixed Income (BND): 3000 (30%) target 40% -> underweight
        # Total: 10000 (100%)

        # Execute divest
        transactions = portfolio.divest()

        # All investments should be sold and cash should be 10000.
        self.assertEqual(portfolio.investments.value, 0.0)
        self.assertEqual(portfolio.cash_value, 10000.0)

        # Verify all transactions are SELL and total sold is 10000.
        self.assertTrue(transactions.buys().empty)
        self.assertEqual(transactions.sells().total_amount, 10000.0)


if __name__ == "__main__":
    unittest.main()
