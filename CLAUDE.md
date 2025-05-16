# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Asset Allocation is a Python tool for managing investment portfolio asset allocation. It helps manage portfolio rebalancing and investment decisions based on target asset allocations.

## Philosophy and Inspiration

This tool is built on several key investment principles:

1. **Optimal Lazy Rebalancing**: The primary approach is to direct new cash to underweighted asset classes (implemented in the `invest` command), minimizing tax consequences in taxable accounts by avoiding unnecessary selling.

2. **Larry Swedroe's 5/25 Rule**: An asset class is considered out of balance if it deviates by an absolute 5% or a relative 25% from its target weight.

3. **Hierarchical Rebalancing**: The tool implements Swedroe's recommendation to check allocations at three levels:
   - Broad asset classes (equities vs fixed income)
   - Geographic categories (domestic vs international)
   - Specific asset categories (small-cap, value, etc.)

4. **Bogleheads Rebalancing Approaches**: Incorporates various rebalancing methodologies from Bogleheads investment philosophy.

## Architecture

The codebase follows a hierarchical structure to represent portfolios:

1. **Portfolio**: The top-level container holding cash and investment assets
   - Contains a hierarchy of asset classes
   - Tracks cash value and target cash value
   - Provides methods for investing excess cash and selling overweight holdings

2. **Asset Classes**: Represent different investment categories
   - **CompositeAssetClass**: Container for nested asset classes
   - **LeafAssetClass**: Container for actual holdings with a target weight

3. **Holdings**: Represent actual securities with ticker symbols and share counts

4. **Visitors Pattern**: Used for traversing the asset class hierarchy
   - Used to create portfolio snapshots and collect data

5. **Services**:
   - **QuoteService**: Provides stock price data (real via yfinance or fake for testing)
   - **PortfolioLoader**: Loads portfolio configuration from YAML files

## Key Concepts

- **Target Weights**: Each asset class has a target allocation percentage
- **Rebalancing Bands**: Uses a 5/25 rule for rebalancing (5% absolute or 25% relative deviation)
- **Prioritized Holdings**: Within each asset class, holdings are prioritized for buy/sell operations
- **Excess Cash**: Cash beyond a target cash reserve that can be invested
- **Optimal Lazy Rebalancing**: Directing new investments to underweight asset classes rather than selling overweight positions
- **Tax-Aware Investing**: The primary mode (`invest`) avoids selling to prevent capital gains taxes in taxable accounts

## Development Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/mattdudys/asset-allocation.git
cd asset-allocation

# Install in development mode with Poetry
poetry install
```

## Common Commands

```bash
# Run the tests
poetry run pytest

# Run specific test files
poetry run pytest tests/test_portfolio.py

# Run specific test cases
poetry run pytest tests/test_portfolio.py::TestPortfolio::test_portfolio_value_sums_children_and_cash

# Install in development mode
pip install -e .

# Run the CLI tool (in development)
poetry run asset-allocation invest data/portfolio_config.yaml
poetry run asset-allocation rebalance data/portfolio_config.yaml
```

## Configuration Format

The tool uses YAML for configuration. A typical configuration file looks like:

```yaml
cash_value: 10000.0          # Current cash in the portfolio
cash_target: 2000.0          # Target cash reserve
holdings:                    # Current holdings with share counts
  AAPL: 10
  MSFT: 5
  # ...
asset_classes:               # Asset class hierarchy with target weights
  - name: US Equity
    target_weight: 0.5
    holdings: ["AAPL", "MSFT", "GOOGL"]
  # ...
```

## Core Commands

1. **invest**: Implements optimal lazy rebalancing by using new cash to buy underweighted assets
   - Tax-efficient approach that avoids selling
   - Primary use case for ongoing portfolio contributions

2. **rebalance**: More aggressive approach that sells overweight positions and reinvests proceeds
   - May trigger capital gains taxes in taxable accounts
   - Useful for tax-advantaged accounts or when portfolio is significantly out of balance

## Formatting

```bash
# Format files with black
poetry run black .
```