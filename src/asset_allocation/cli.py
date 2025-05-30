"""Command line interface for asset allocation."""

import argparse
from typing import Optional

import pandas as pd

from asset_allocation.portfolio import Portfolio
from asset_allocation.quote_service import BatchYFinanceQuoteService
from asset_allocation.snapshot import PortfolioSnapshot
from asset_allocation.transaction import Transactions
from .portfolio_loader import PortfolioLoader


def print_snapshot(snapshot: PortfolioSnapshot):
    print(f"Total value: ${snapshot.value:,.2f}")
    print(f"Investible value: ${snapshot.investible_value:,.2f}")
    print(f"Cash: ${snapshot.cash:,.2f}")
    print(f"Excess cash: ${snapshot.excess_cash:,.2f}")
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


def print_transactions(transaction_log: Transactions):
    df = transaction_log.to_dataframe()
    if not df.empty:
        print("Transactions:")
        df["type"] = df["type"].astype(str)
        df["price"] = df["price"].apply(lambda x: f"${x:,.2f}")
        df = df.groupby(["type", "ticker", "price"]).sum()
        df["amount"] = df["amount"].apply(lambda x: f"${x:,.2f}")
        print(df)


def invest_excess_cash(portfolio: Portfolio):
    """Invest excess cash in the portfolio."""
    starting_snapshot = portfolio.snapshot()
    print("=== Before ===")
    print_snapshot(starting_snapshot)
    print()
    print("Investing excess cash...")
    transaction_log = portfolio.invest_excess_cash()
    if transaction_log.empty:
        print("Not enough excess cash to buy anything. No transactions were made.")
    else:
        ending_snapshot = portfolio.snapshot()
        print(
            f"Invested ${starting_snapshot.cash - ending_snapshot.cash:,.2f} of excess cash."
        )
        print()
        print_transactions(transaction_log)
        print()
        print("=== After ===")
        print_snapshot(ending_snapshot)


def divest_portfolio(portfolio: Portfolio):
    """Sell overweight holdings to reach cash target."""
    starting_snapshot = portfolio.snapshot()
    print("=== Before ===")
    print_snapshot(starting_snapshot)
    print()
    print("Selling overweight holdings to reach cash target...")
    transaction_log = portfolio.divest()
    ending_snapshot = portfolio.snapshot()
    print()
    print_transactions(transaction_log)
    print()
    print("=== After ===")
    print_snapshot(ending_snapshot)


def rebalance(portfolio: Portfolio):
    """Sell overweight holdings in the portfolio."""
    starting_snapshot = portfolio.snapshot()
    print("=== Before ===")
    print_snapshot(starting_snapshot)
    print()
    print("Selling overweight holdings...")
    transaction_log = portfolio.sell_overweight()
    snapshot2 = portfolio.snapshot()
    print()
    print_transactions(transaction_log)
    print()
    print("=== After selling overweight holdings ===")
    print_snapshot(snapshot2)
    print()
    print("Investing excess cash...")
    transaction_log = portfolio.invest_excess_cash(transaction_log)
    if transaction_log.empty:
        print("Not enough excess cash to buy anything. No transactions were made.")
    else:
        ending_snapshot = portfolio.snapshot()
        print(f"Invested ${snapshot2.cash - ending_snapshot.cash:,.2f} of excess cash.")
        print()
        print_transactions(transaction_log)
        print()
        print("=== After ===")
        print_snapshot(ending_snapshot)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Asset Allocation Portfolio Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    invest_parser = subparsers.add_parser(
        "invest", help="Invest excess cash according to target allocations"
    )
    invest_parser.add_argument("config", help="Path to the YAML configuration file")

    divest_parser = subparsers.add_parser(
        "divest", help="Sell overweight holdings to reach cash target and reinvest"
    )
    divest_parser.add_argument("config", help="Path to the YAML configuration file")

    rebalance_parser = subparsers.add_parser(
        "rebalance", help="Sell overweight holdings and rebalance portfolio"
    )
    rebalance_parser.add_argument("config", help="Path to the YAML configuration file")

    args = parser.parse_args()

    loader = PortfolioLoader(BatchYFinanceQuoteService())
    portfolio = loader.load(args.config)

    if args.command == "invest":
        invest_excess_cash(portfolio)
    elif args.command == "divest":
        divest_portfolio(portfolio)
    elif args.command == "rebalance":
        rebalance(portfolio)


if __name__ == "__main__":
    main()
