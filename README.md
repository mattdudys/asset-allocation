# Asset Allocation

A Python tool for managing investment portfolio asset allocation. This tool helps track, analyze, and rebalance investment portfolios according to target asset allocations.

## Features

- Define hierarchical asset classes with target allocations
- Track current portfolio value and allocation percentages
- Invest excess cash according to target allocations
- Rebalance overweight/underweight positions
- Automatically fetch current market prices via Yahoo Finance
- Support for nested asset classes (e.g., US Equity, International Bonds)
- Uses bid/ask prices for more accurate buy/sell operations

## Installation

```bash
# Clone the repository
git clone https://github.com/mattdudys/asset-allocation.git
cd asset-allocation

# Install in development mode
pip install -e .
# Or with Poetry
poetry install
```

## Usage

```bash
# Invest excess cash according to target allocations
asset-allocation invest path/to/config.yaml

# Sell overweight holdings and invest excess cash to rebalance portfolio
asset-allocation rebalance path/to/config.yaml

# Sell most overweight holdings to reach cash target
asset-allocation divest path/to/config.yaml
```

## Configuration

The tool uses YAML for configuration. A sample configuration file:

```yaml
# Current and target cash values
cash_value: 5000.0
cash_target: 2000.0

# Current holdings (ticker: shares)
holdings:
  VTI: 100   # Vanguard Total US Stock Market ETF
  VXUS: 80   # Vanguard Total International Stock ETF
  BND: 70    # Vanguard Total US Bond Market ETF

# Asset class hierarchy with target weights
asset_classes:
  - name: Equity
    asset_classes:
      - name: US Equity
        target_weight: 0.40
        holdings: ["VTI"]
      - name: International Equity
        target_weight: 0.20
        holdings: ["VXUS"]
  - name: Fixed Income
    target_weight: 0.40
    holdings: ["BND"]
```

This example represents a classic three-fund portfolio following Bogleheads principles:
- 60% in equities (40% US, 20% international)
- 40% in bonds
- Each asset class represented by a single low-cost, broad-market ETF

## Development

```bash
# Run tests
poetry run python -m unittest discover tests

# Run specific test files
poetry run python -m unittest tests/test_portfolio.py

# Format code
poetry run black .
```

## How It Works

### Philosophical Approach

This tool implements "optimal lazy rebalancing" strategies based on several key principles:

1. **Avoid Selling in Taxable Accounts**: The primary `invest` command focuses on directing new cash to underweighted asset classes, minimizing tax events by avoiding sales when possible.

2. **Hierarchical Rebalancing**: Following Larry Swedroe's approach, the tool checks allocation at three levels:
   - Broad asset classes (e.g., equities vs fixed income)
   - Geographic categories (domestic vs international)
   - Specific asset categories (small-cap, value, etc.)

3. **5/25 Rebalance Rule**: An asset class is considered out of balance if it deviates by an absolute 5% or a relative 25% from its target weight, a widely respected threshold popularized by Swedroe.

### Rebalancing Process

When investing excess cash or rebalancing:
1. The most underweight asset classes receive new investments first
2. When selling, the most overweight asset classes are sold first 
3. Within each asset class, holdings are processed in the order specified in the configuration

### Two Core Commands

- **invest**: Implements optimal lazy rebalancing by using new cash to buy underweighted assets
- **rebalance**: More aggressive approach that sells overweight positions and reinvests proceeds
- **divest**: Sells overweight holdings until the cash target is met

## Inspiration

This tool is inspired by principles from:
- [Optimal Rebalancing](https://optimalrebalancing.info/) strategies for tax-efficient portfolio management
- [Bogleheads Wiki](https://www.bogleheads.org/wiki/Rebalancing) approaches to rebalancing methodologies
- Larry Swedroe's 5/25 rule and hierarchical rebalancing approach

## License

MIT