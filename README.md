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

The tool follows the 5/25 rule for rebalancing - it considers an asset class out of balance if it deviates by an absolute 5% or a relative 25% from its target weight.

When investing excess cash or rebalancing:
1. The most underweight asset classes receive new investments first
2. When selling, the most overweight asset classes are sold first 
3. Within each asset class, holdings are processed in the order specified in the configuration

## License

MIT