# General Project Instructions for Asset Allocation

This project is a Python tool for managing investment portfolio asset allocation. It helps manage portfolio rebalancing and investment decisions based on target asset allocations.

**Technologies:**
- Primary Language: Python
- Key Libraries/Tools: Poetry, unittest, black, PyYAML, yfinance, pandas

**Coding Style:**
- Adhere to PEP 8 guidelines.
- Use `black` for code formatting.
- Include type hints for functions and methods.

**Core Domain Concepts:**
- **Asset Class:** Represents investment categories. Can be `CompositeAssetClass` (container for nested classes) or `LeafAssetClass` (container for holdings).
- **Holding:** Represents an actual security with a ticker symbol and share count.
- **Target Weight:** The desired allocation percentage for an asset class.
- **Portfolio:** The top-level container for cash and asset classes.
- **Rebalancing:** The process of adjusting portfolio allocations back to target weights.
    - **Optimal Lazy Rebalancing:** Directing new cash to underweighted asset classes (`invest` command).
    - **5/25 Rule:** An asset class is out of balance if it deviates by an absolute 5% or a relative 25% from its target weight.
    - **Hierarchical Rebalancing:** Checking allocations at broad, geographic, and specific asset category levels.
- **`invest` command:** Implements optimal lazy rebalancing using new cash.
- **`rebalance` command:** More aggressive approach that may involve selling overweight positions.
- **Visitor Pattern:** Used for traversing the asset class hierarchy (e.g., for creating snapshots).
