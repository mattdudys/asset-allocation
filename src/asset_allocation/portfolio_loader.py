from typing import Dict
import yaml
from .portfolio import Portfolio
from .asset_class import AssetClass, CompositeAssetClass, LeafAssetClass
from .holding import Holding
from .quote_service import QuoteService, FakeQuoteService


class PortfolioLoader:
    """Loads portfolio configuration from YAML files."""

    def __init__(self, quote_service: QuoteService = None):
        self.quote_service = quote_service or FakeQuoteService({})

    def _load_portfolio_data(self, config_file: str) -> dict:
        """Load the combined portfolio data from a YAML file."""
        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def _tickers_within_asset_classes(self, data: dict) -> set[str]:
        """Extract tickers from the asset class hierarchy without constructing the tree."""
        tickers = set()
        # If data contains "investments", or "asset_classes", it's a composite node.
        asset_classes = data.get("investments", []) + data.get("asset_classes", [])
        if asset_classes:
            for asset_class in asset_classes:
                tickers.update(self._tickers_within_asset_classes(asset_class))
        elif "holdings" in data:
            # Leaf node with holdings
            tickers.update(data.get("holdings", []))
        return tickers

    def _create_asset_class(self, data: dict, holdings: Dict[str, int]) -> AssetClass:
        """Create an AssetClass from the hierarchy data."""
        name = data["name"]

        # If this is a composite node (has subcategories)
        if "asset_classes" in data:
            children = [
                self._create_asset_class(child, holdings)
                for child in data["asset_classes"]
            ]
            return CompositeAssetClass(name, children)

        # Otherwise it's a leaf node with holdings
        target_weight = data["target_weight"]
        holding_objects = []
        for ticker in data["holdings"]:
            if ticker in holdings:
                shares = holdings[ticker]
                price = self.quote_service.get_price(ticker)
                holding_objects.append(Holding(ticker, shares, price))

        return LeafAssetClass(name, target_weight, holding_objects)

    def load(self, config_file: str) -> Portfolio:
        """Load a portfolio from a single YAML configuration file.

        Args:
            config_file: Path to the YAML file containing portfolio data.
        """
        data = self._load_portfolio_data(config_file)

        # Extract cash values
        cash_value = data.get("cash_value", 0.0)
        cash_target = data.get("cash_target", 0.0)

        # Download prices for all tickers referenced in one batch.
        tickers = self._tickers_within_asset_classes(data) | set(
            data.get("holdings", {}).keys()
        )
        self.quote_service.cache(list(tickers))

        # Create the asset class hierarchy
        children = [
            self._create_asset_class(investment, data["holdings"])
            for investment in data["investments"]
        ]

        return Portfolio(
            cash_value=cash_value, cash_target=cash_target, children=children
        )
