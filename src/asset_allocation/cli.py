"""Command line interface for asset allocation."""

import argparse

from asset_allocation.quote_service import YFinanceQuoteService
from .portfolio import Portfolio
from .portfolio_loader import PortfolioLoader


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Asset Allocation Portfolio Manager")
    parser.add_argument("--config", help="Path to asset class hierarchy YAML file")
    parser.add_argument("--holdings", help="Path to current holdings YAML file")
    parser.add_argument("--invest-excess-cash", action="store_true", help="Invest excess cash according to target allocations")
    args = parser.parse_args()

    if args.config and args.holdings:
        loader = PortfolioLoader(YFinanceQuoteService())
        portfolio = loader.load(args.config, args.holdings)
        print(f"Loaded portfolio with value: ${portfolio.value:,.2f}")
        
        if args.invest_excess_cash:
            starting_cash = portfolio.cash_value
            transaction_log = portfolio.invest_excess_cash()
            ending_cash = portfolio.cash_value
            print(f"Invested ${starting_cash - ending_cash:,.2f} of excess cash")
            print(transaction_log.to_dataframe().groupby(["type", "ticker", "price"]).sum())
    else:
        print("Please provide both --config and --holdings files")


if __name__ == "__main__":
    main() 