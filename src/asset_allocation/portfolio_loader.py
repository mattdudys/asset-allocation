from typing import Dict, List, Union
import yaml
from .portfolio import Portfolio
from .asset_class import AssetClass, AssetClassCategory
from .holding import Holding
from .quote_service import QuoteService, FakeQuoteService


class PortfolioLoader:
    """Loads portfolio configuration from YAML files."""

    def __init__(self, quote_service: QuoteService = None):
        self.quote_service = quote_service or FakeQuoteService({})

    def _load_asset_class_hierarchy(self, config_file: str) -> dict:
        """Load the asset class hierarchy from a YAML file."""
        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def _load_holdings(self, holdings_file: str) -> dict:
        """Load the current holdings from a YAML file."""
        with open(holdings_file, "r") as f:
            return yaml.safe_load(f)

    def _create_asset_class_or_category(
        self, data: dict, holdings: Dict[str, int]
    ) -> Union[AssetClass, AssetClassCategory]:
        """Create an AssetClass or AssetClassCategory from the hierarchy data."""
        name = data["name"]

        # If this is a category (has subcategories)
        if "categories" in data:
            children = [
                self._create_asset_class_or_category(child, holdings)
                for child in data["categories"]
            ]
            return AssetClassCategory(name, children)

        # Otherwise it's an asset class with holdings
        target_weight = data["target_weight"]  # Only leaf nodes have target weights
        holding_objects = []
        for ticker in data["holdings"]:
            if ticker in holdings:
                shares = holdings[ticker]
                price = self.quote_service.get_price(ticker)
                holding_objects.append(Holding(ticker, shares, price))

        return AssetClass(name, target_weight, holding_objects)

    def load(self, config_file: str, holdings_file: str) -> Portfolio:
        """Load a portfolio from configuration and holdings YAML files.
        
        Args:
            config_file: Path to the YAML file containing asset class hierarchy
            holdings_file: Path to the YAML file containing current holdings
        """
        hierarchy_data = self._load_asset_class_hierarchy(config_file)
        holdings_data = self._load_holdings(holdings_file)

        # Extract cash values
        cash_value = holdings_data.get("cash_value", 0.0)
        cash_target = hierarchy_data.get("cash_target", 0.0)

        # Create the asset class hierarchy
        children = [
            self._create_asset_class_or_category(
                investment, holdings_data["holdings"]
            )
            for investment in hierarchy_data["investments"]
        ]

        return Portfolio(cash_value=cash_value, cash_target=cash_target, children=children)
