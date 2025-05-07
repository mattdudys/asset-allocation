"""Command line interface for asset allocation."""

import argparse

import pandas as pd

from asset_allocation.quote_service import YFinanceQuoteService
from asset_allocation.snapshot import PortfolioSnapshot
from asset_allocation.transaction import TransactionLog
from .portfolio_loader import PortfolioLoader


def print_snapshot(snapshot: PortfolioSnapshot):
    df = pd.DataFrame(snapshot.asset_classes)
    # Format value column as currency.
    df["value"] = df["value"].apply(lambda x: f"${x:,.2f}")
    # Format target weight, actual weight, and fractional deviation columns as percentages.
    df["target_weight"] = df["target_weight"].apply(lambda x: f"{x:.2%}")
    df["actual_weight"] = df["actual_weight"].apply(lambda x: f"{x:.2%}")
    df["fractional_deviation"] = df["fractional_deviation"].apply(lambda x: f"{x:.2%}")
    df["underweight"] = df["underweight"].apply(lambda x: "X" if x else "")
    df["overweight"] = df["overweight"].apply(lambda x: "X" if x else "")
    print(df.to_string(index=False))


def print_transaction_log(transaction_log: TransactionLog):
    df = transaction_log.to_dataframe()
    if df:
        print(df.groupby(["type", "ticker", "price"]).sum())


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Asset Allocation Portfolio Manager")
    parser.add_argument(
        "--config", help="Path to asset class hierarchy YAML file", required=True
    )
    parser.add_argument(
        "--holdings", help="Path to current holdings YAML file", required=True
    )
    parser.add_argument(
        "--invest-excess-cash",
        action="store_true",
        help="Invest excess cash according to target allocations",
    )
    args = parser.parse_args()

    loader = PortfolioLoader(YFinanceQuoteService())
    portfolio = loader.load(args.config, args.holdings)
    print(f"Portfolio:")
    print(f"  Total value: ${portfolio.value:,.2f}")
    print(f"  Investible value: ${portfolio.investible_value:,.2f}")
    print(f"  Cash: ${portfolio.cash_value:,.2f}")
    print(f"  Excess cash: ${portfolio.excess_cash:,.2f}")
    starting_snapshot = portfolio.snapshot()
    print_snapshot(starting_snapshot)
    print()

    if args.invest_excess_cash:
        transaction_log = portfolio.invest_excess_cash()
        if transaction_log.empty:
            print("Not enough excess cash to invest. No transactions were made.")
        else:
            ending_snapshot = portfolio.snapshot()
            print(
                f"Invested ${starting_snapshot.cash - ending_snapshot.cash:,.2f} of excess cash"
            )
            print_transaction_log(transaction_log)
            print_snapshot(ending_snapshot)


if __name__ == "__main__":
    main()
