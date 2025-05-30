# Product Requirements Document: Bid/Ask Price Implementation

## Introduction/Overview
Currently, the asset allocation system uses a single price for all operations (valuation, buying, and selling) of holdings. This can lead to inaccurate investment decisions, as demonstrated by market orders executing at different prices than predicted. This feature will implement separate bid and ask prices to improve the accuracy of buy/sell operations while maintaining the current market price for valuation purposes.

## Goals
1. Improve the accuracy of buy/sell price predictions by using bid prices for selling and ask prices for buying
2. Maintain current market price for holding valuation
3. Enhance the QuoteService implementations to efficiently fetch and cache bid/ask prices
4. Ensure the system gracefully handles bid/ask price anomalies

## User Stories
1. As an investor, I want to see more accurate buy prices so that my investment decisions better match actual market execution
2. As an investor, I want to see more accurate sell prices so that I can better predict my available cash from sales
3. As a user, I want the system to maintain its current performance when fetching price data
4. As a user, I want to be warned if there are any anomalies in the bid/ask prices

## Functional Requirements
1. The QuoteService interface must be extended to support:
   - Getting bid price
   - Getting ask price
   - Getting current market price (existing functionality)

2. The Holding class must be modified to:
   - Store separate bid and ask prices
   - Use ask price for buy operations
   - Use bid price for sell operations
   - Continue using current market price for value calculations

3. YFinanceQuoteService must be updated to:
   - Cache the yfinance.Ticker.info dictionary
   - Extract bid and ask prices from the info dictionary, using the `bid` and `ask` keys
   - Maintain backward compatibility with existing price fetching

4. BatchYFinanceQuoteService must be updated to:
   - Include bid and ask prices in its batch request using the `Low` and `High` columns
   - Cache bid and ask prices along with current market price

5. The system must:
   - Print a warning if bid price is higher than ask price
   - Raise an error if bid or ask prices are unavailable
   - Maintain the current transaction price recording (single price)

## Non-Goals (Out of Scope)
1. Real-time price updates during program execution
2. Modifying the Transaction class to record bid/ask prices
3. Implementing complex price validation or correction logic
4. Adding support for different types of orders (market, limit, etc.)
5. Modifying the holding valuation logic to use bid/ask prices

## Technical Considerations
1. QuoteService Interface Changes:
   ```python
   class QuoteService:
       def get_bid_price(self, ticker: str) -> float: ...
       def get_ask_price(self, ticker: str) -> float: ...
       def get_price(self, ticker: str) -> float: ...  # existing method
   ```

2. Holding Class Changes:
   ```python
   class Holding:
       def __init__(self, ticker: str, shares: float, price: float, bid_price: float, ask_price: float): ...
       def buy(self, budget: float) -> Optional[Transaction]:  # uses ask_price
       def sell(self) -> Optional[Transaction]:  # uses bid_price
       @property
       def value(self) -> float:  # continues using price
   ```

3. Performance Considerations:
   - YFinanceQuoteService should cache the Ticker.info dictionary
   - BatchYFinanceQuoteService should maintain its efficient batch request pattern
   - No additional API calls should be required for bid/ask prices

## Success Metrics
1. The difference between predicted and actual execution prices for market orders should be reduced
2. The system should maintain its current performance characteristics
3. All existing functionality should continue to work as expected

## Open Questions
1. Should we add any logging or monitoring to track the bid/ask spread over time?
No.
2. Should we consider adding a configuration option to adjust the bid/ask prices (e.g., add a small buffer) to account for market movement?
No.
3. Should we add any validation for minimum bid/ask spread to detect potential data issues?
Print a warning if bid is higher than ask. Print a warning if the bid > market price and if ask < market price. Also print a warning if the spread is large, say 5% of the market price.

## Implementation Notes
1. The implementation should be done in phases:
   a. Update QuoteService interface and implementations
   b. Modify Holding class to use bid/ask prices
   c. Add warning for bid > ask price
   d. Update tests and documentation

2. Testing should include:
   - Unit tests for new bid/ask price functionality
   - Integration tests with actual yfinance data
   - Edge case tests for bid/ask anomalies

3. Testing does not need to include:
   - Performance tests