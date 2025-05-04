from typing import Dict, List, Union
import yaml
from .portfolio import Portfolio
from .asset_class import AssetClass, AssetClassCategory
from .holding import Holding
from .quote_service import QuoteService


def load_asset_class_hierarchy(hierarchy_file: str) -> dict:
    """Load the asset class hierarchy from a YAML file."""
    with open(hierarchy_file, "r") as f:
        return yaml.safe_load(f)


def load_holdings(holdings_file: str) -> dict:
    """Load the current holdings from a YAML file."""
    with open(holdings_file, "r") as f:
        return yaml.safe_load(f)


def create_asset_class_or_category(
    data: dict, holdings: Dict[str, int], quote_service: QuoteService
) -> Union[AssetClass, AssetClassCategory]:
    """Create an AssetClass or AssetClassCategory from the hierarchy data."""
    name = data["name"]

    # If this is a category (has subcategories)
    if "categories" in data:
        children = [
            create_asset_class_or_category(child, holdings, quote_service)
            for child in data["categories"]
        ]
        return AssetClassCategory(name, children)

    # Otherwise it's an asset class with holdings
    target_weight = data["target_weight"]  # Only leaf nodes have target weights
    holding_objects = []
    for ticker in data["holdings"]:
        if ticker in holdings:
            shares = holdings[ticker]
            price = quote_service.get_price(ticker)
            holding_objects.append(Holding(ticker, shares, price))

    return AssetClass(name, target_weight, holding_objects)


def load_portfolio(
    hierarchy_file: str, holdings_file: str, quote_service: QuoteService
) -> Portfolio:
    """Load a portfolio from hierarchy and holdings YAML files."""
    hierarchy_data = load_asset_class_hierarchy(hierarchy_file)
    holdings_data = load_holdings(holdings_file)

    # Extract cash values
    cash_value = holdings_data.get("cash_value", 0.0)
    cash_target = hierarchy_data.get(
        "cash_target", 0.0
    )  # Default to 0.0 if not specified

    # Create the asset class hierarchy
    children = [
        create_asset_class_or_category(
            investment, holdings_data["holdings"], quote_service
        )
        for investment in hierarchy_data["investments"]
    ]

    return Portfolio(cash_value=cash_value, cash_target=cash_target, children=children)
