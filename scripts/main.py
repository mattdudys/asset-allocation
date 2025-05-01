from asset_allocation import HoldingGroup, CashHolding, TickerHolding


def main():
    portfolio = HoldingGroup(
        "Portfolio", [CashHolding(9000.00), HoldingGroup("Equities", [])]
    )


if __name__ == "__main__":
    main()
