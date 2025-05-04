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
    parser.add_argument("--rebalance", action="store_true", help="Rebalance the portfolio")
    args = parser.parse_args()

    if args.config and args.holdings:
        loader = PortfolioLoader(YFinanceQuoteService())
        portfolio = loader.load(args.config, args.holdings)
        print(f"Loaded portfolio with value: ${portfolio.value:,.2f}")
        
        if args.rebalance:
            print("Rebalancing portfolio...")
            # TODO: Implement rebalancing logic
    else:
        print("Please provide both --config and --holdings files")


if __name__ == "__main__":
    main() 