import unittest
from asset_allocation.holding import Holding
from asset_allocation.asset_class import LeafAssetClass, CompositeAssetClass
from asset_allocation.portfolio import Portfolio
from asset_allocation.snapshot import (
    AssetClassSnapshot,
    HoldingSnapshot,
    PortfolioSnapshot,
    PortfolioSnapshotter,
)


class TestSnapshots(unittest.TestCase):
    """Tests for snapshot data classes."""

    def test_asset_class_snapshot_creation(self):
        """Test creating an AssetClassSnapshot with proper values."""
        snapshot = AssetClassSnapshot(
            name="US Equity",
            value=5000.0,
            target_weight=0.5,
            actual_weight=0.6,
            fractional_deviation=0.2,
            underweight=False,
            overweight=True,
        )

        self.assertEqual(snapshot.name, "US Equity")
        self.assertEqual(snapshot.value, 5000.0)
        self.assertEqual(snapshot.target_weight, 0.5)
        self.assertEqual(snapshot.actual_weight, 0.6)
        self.assertEqual(snapshot.fractional_deviation, 0.2)
        self.assertFalse(snapshot.underweight)
        self.assertTrue(snapshot.overweight)

    def test_holding_snapshot_creation(self):
        """Test creating a HoldingSnapshot with proper values."""
        snapshot = HoldingSnapshot(name="VOO", value=10000.0, shares=25.0)

        self.assertEqual(snapshot.name, "VOO")
        self.assertEqual(snapshot.value, 10000.0)
        self.assertEqual(snapshot.shares, 25.0)

    def test_portfolio_snapshot_creation(self):
        """Test creating a PortfolioSnapshot with proper values."""
        asset_class_snapshot = AssetClassSnapshot(
            name="US Equity",
            value=5000.0,
            target_weight=0.5,
            actual_weight=0.6,
            fractional_deviation=0.2,
            underweight=False,
            overweight=True,
        )

        holding_snapshot = HoldingSnapshot(name="VOO", value=5000.0, shares=25.0)

        snapshot = PortfolioSnapshot(
            cash=1000.0,
            value=6000.0,
            investible_value=5500.0,
            excess_cash=500.0,
            asset_classes=[asset_class_snapshot],
            holdings=[holding_snapshot],
        )

        self.assertEqual(snapshot.cash, 1000.0)
        self.assertEqual(snapshot.value, 6000.0)
        self.assertEqual(snapshot.investible_value, 5500.0)
        self.assertEqual(snapshot.excess_cash, 500.0)
        self.assertEqual(len(snapshot.asset_classes), 1)
        self.assertEqual(len(snapshot.holdings), 1)
        self.assertEqual(snapshot.asset_classes[0].name, "US Equity")
        self.assertEqual(snapshot.holdings[0].name, "VOO")


class TestPortfolioSnapshotter(unittest.TestCase):
    """Tests for the PortfolioSnapshotter visitor."""

    def test_snapshotter_captures_portfolio_state(self):
        """Test that the snapshotter correctly captures the portfolio state."""
        # Create a simple portfolio
        holding = Holding("VOO", 25, price=400.0)
        asset_class = LeafAssetClass("US Equity", target_weight=1.0, children=[holding])
        portfolio = Portfolio(
            cash_value=1000.0, cash_target=500.0, children=[asset_class]
        )

        # Create a snapshot
        visitor = PortfolioSnapshotter(portfolio)
        portfolio.investments.visit(visitor)
        snapshot = visitor.snapshot

        # Verify snapshot contains correct portfolio values
        self.assertEqual(snapshot.cash, 1000.0)
        self.assertEqual(snapshot.value, 11000.0)  # 10000 (holdings) + 1000 (cash)
        self.assertEqual(
            snapshot.investible_value, 10500.0
        )  # 10000 (holdings) + 500 (excess cash)
        self.assertEqual(snapshot.excess_cash, 500.0)

        # Verify asset class snapshots (root node "Total" + US Equity)
        self.assertEqual(len(snapshot.asset_classes), 2)

        # Find the US Equity asset class snapshot
        us_equity_snapshot = None
        for ac in snapshot.asset_classes:
            if ac.name == "US Equity":
                us_equity_snapshot = ac
                break

        self.assertIsNotNone(
            us_equity_snapshot, "US Equity asset class snapshot should exist"
        )
        self.assertEqual(us_equity_snapshot.value, 10000.0)
        self.assertEqual(us_equity_snapshot.target_weight, 1.0)
        self.assertAlmostEqual(us_equity_snapshot.actual_weight, 10000.0 / 10500.0)

        # Verify holding snapshot
        self.assertEqual(len(snapshot.holdings), 1)
        h_snapshot = snapshot.holdings[0]
        self.assertEqual(h_snapshot.name, "VOO")
        self.assertEqual(h_snapshot.value, 10000.0)
        self.assertEqual(h_snapshot.shares, 25)

    def test_snapshotter_with_complex_hierarchy(self):
        """Test snapshotter with a more complex hierarchy of asset classes."""
        # Create a portfolio with nested asset classes
        holding1 = Holding("VOO", 10, price=400.0)  # 4000
        holding2 = Holding("VIOV", 20, price=200.0)  # 4000
        us_stocks = LeafAssetClass("US Stocks", target_weight=0.4, children=[holding1])
        intl_stocks = LeafAssetClass(
            "International Stocks", target_weight=0.2, children=[holding2]
        )
        stocks = CompositeAssetClass("Stocks", [us_stocks, intl_stocks])

        holding3 = Holding("VGIT", 40, price=100.0)  # 4000
        bonds = LeafAssetClass("Bonds", target_weight=0.4, children=[holding3])

        portfolio = Portfolio(
            cash_value=2000.0, cash_target=1000.0, children=[stocks, bonds]
        )

        # Create a snapshot
        visitor = PortfolioSnapshotter(portfolio)
        portfolio.investments.visit(visitor)
        snapshot = visitor.snapshot

        # Verify snapshot contains correct portfolio values
        self.assertEqual(snapshot.cash, 2000.0)
        self.assertEqual(snapshot.value, 14000.0)  # 12000 (holdings) + 2000 (cash)
        self.assertEqual(
            snapshot.investible_value, 13000.0
        )  # 12000 (holdings) + 1000 (excess cash)
        self.assertEqual(snapshot.excess_cash, 1000.0)

        # Verify asset class snapshots are created for all nodes in the hierarchy
        # "Total" + "Stocks" + "US Stocks" + "International Stocks" + "Bonds" = 5 snapshots
        self.assertEqual(len(snapshot.asset_classes), 5)

        # Verify all holdings are captured
        self.assertEqual(len(snapshot.holdings), 3)  # 3 holdings in total

        # Check that we have snapshots for all asset classes
        asset_class_names = [ac.name for ac in snapshot.asset_classes]
        self.assertIn("US Stocks", asset_class_names)
        self.assertIn("International Stocks", asset_class_names)
        self.assertIn("Bonds", asset_class_names)
        self.assertIn("Stocks", asset_class_names)

        # Check that we have snapshots for all holdings
        holding_names = [h.name for h in snapshot.holdings]
        self.assertIn("VOO", holding_names)
        self.assertIn("VIOV", holding_names)
        self.assertIn("VGIT", holding_names)

        # Verify values are correct for leaf asset classes
        for ac in snapshot.asset_classes:
            if ac.name == "US Stocks":
                self.assertEqual(ac.value, 4000.0)
                self.assertEqual(ac.target_weight, 0.4)
            elif ac.name == "International Stocks":
                self.assertEqual(ac.value, 4000.0)
                self.assertEqual(ac.target_weight, 0.2)
            elif ac.name == "Bonds":
                self.assertEqual(ac.value, 4000.0)
                self.assertEqual(ac.target_weight, 0.4)


if __name__ == "__main__":
    unittest.main()
