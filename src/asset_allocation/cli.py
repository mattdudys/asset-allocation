"""Command line interface for asset allocation."""

import argparse

import pandas as pd

from asset_allocation.quote_service import YFinanceQuoteService
from asset_allocation.snapshot import PortfolioSnapshot
from asset_allocation.transaction import TransactionLog
from .portfolio_loader import PortfolioLoader


def print_snapshot(snapshot: PortfolioSnapshot):
    print(pd.DataFrame(snapshot.asset_classes))


def print_transaction_log(transaction_log: TransactionLog):
    print(transaction_log.to_dataframe().groupby(["type", "ticker", "price"]).sum())


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Asset Allocation Portfolio Manager")
    parser.add_argument("--config", help="Path to asset class hierarchy YAML file")
    parser.add_argument("--holdings", help="Path to current holdings YAML file")
    parser.add_argument(
        "--invest-excess-cash",
        action="store_true",
        help="Invest excess cash according to target allocations",
    )
    args = parser.parse_args()

    if args.config and args.holdings:
        loader = PortfolioLoader(YFinanceQuoteService())
        portfolio = loader.load(args.config, args.holdings)
        print(f"Loaded portfolio with value: ${portfolio.value:,.2f}")
        starting_snapshot = portfolio.snapshot()

        if args.invest_excess_cash:
            print_snapshot(starting_snapshot)
            transaction_log = portfolio.invest_excess_cash()
            ending_snapshot = portfolio.snapshot()
            print(
                f"Invested ${starting_snapshot.cash - ending_snapshot.cash:,.2f} of excess cash"
            )
            print_transaction_log(transaction_log)
            print_snapshot(ending_snapshot)
    else:
        print("Please provide both --config and --holdings files")


if __name__ == "__main__":
    main()
