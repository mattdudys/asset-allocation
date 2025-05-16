# Asset Allocation

A Python tool for managing investment portfolio asset allocation. This tool helps track, analyze, and rebalance investment portfolios according to target asset allocations.

## Features

- Define hierarchical asset classes with target allocations
- Track current portfolio value and allocation percentages
- Invest excess cash according to target allocations
- Rebalance overweight/underweight positions
- Automatically fetch current market prices via Yahoo Finance
- Support for nested asset classes (e.g., US Equity, International Bonds)

## Installation

```bash
# Install from PyPI
pip install asset-allocation

# Development installation with Poetry
poetry install
```

## Usage

```bash
# Invest excess cash according to target allocations
asset-allocation invest path/to/config.yaml

# Sell overweight holdings and rebalance portfolio
asset-allocation rebalance path/to/config.yaml
```

## Configuration

The tool uses YAML for configuration. A sample configuration file:

```yaml
# Current and target cash values
cash_value: 10000.0
cash_target: 2000.0

# Current holdings (ticker: shares)
holdings:
  AAPL: 10
  MSFT: 5
  GOOGL: 2
  AGG: 20
  BNDX: 10

# Asset class hierarchy with target weights
asset_classes:
  - name: US Equity
    target_weight: 0.5
    holdings: ["AAPL", "MSFT", "GOOGL"]
  - name: Fixed Income
    asset_classes:
      - name: US Bonds
        target_weight: 0.3
        holdings: ["AGG"]
      - name: International Bonds
        target_weight: 0.2
        holdings: ["BNDX"]
```

## Development

```bash
# Clone the repository
git clone https://github.com/mattdudys/asset-allocation.git
cd asset-allocation

# Install in development mode
pip install -e .
# Or with Poetry
poetry install

# Run tests
poetry run pytest

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

## Inspiration

This tool is inspired by principles from:
- [Optimal Rebalancing](https://optimalrebalancing.info/) strategies for tax-efficient portfolio management
- [Bogleheads Wiki](https://www.bogleheads.org/wiki/Rebalancing) approaches to rebalancing methodologies
- Larry Swedroe's 5/25 rule and hierarchical rebalancing approach

## License

MIT