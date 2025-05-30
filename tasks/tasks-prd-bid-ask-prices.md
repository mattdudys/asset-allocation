# Task List: Bid/Ask Price Implementation

## Relevant Files

- `src/asset_allocation/quote_service.py` - Contains the QuoteService interface and base implementations
- `tests/test_quote_service.py` - Unit tests for quote service implementations
- `src/asset_allocation/holding.py` - Contains the Holding class implementation
- `tests/test_holding.py` - Unit tests for the Holding class
- `src/asset_allocation/quote_service.py` - Contains both YFinanceQuoteService and BatchYFinanceQuoteService implementations
- `tests/test_quote_service.py` - Unit tests for both quote service implementations

## Tasks

- [x] 1.0 Update QuoteService Interface and Base Implementation
  - [x] 1.1 Add new methods to QuoteService interface:
    - [x] Add `get_bid_price(ticker: str) -> float`
    - [x] Add `get_ask_price(ticker: str) -> float`
    - [x] Update docstrings for all methods
  - [x] 1.2 Update any base implementations to raise NotImplementedError for new methods
  - [x] 1.3 Update type hints and documentation

- [ ] 2.0 Modify YFinanceQuoteService Implementation
  - [ ] 2.1 Add caching for Ticker.info dictionary
    - [ ] Add instance variable to store cached info
    - [ ] Modify `get_price` to use cached info
  - [ ] 2.2 Implement new bid/ask price methods
    - [ ] Implement `get_bid_price` using 'bid' key from info dictionary
    - [ ] Implement `get_ask_price` using 'ask' key from info dictionary
  - [ ] 2.3 Add simple error handling
    - [ ] Raise ValueError with descriptive message if bid/ask prices are missing from info dictionary
  - [ ] 2.4 Update tests
    - [ ] Test bid/ask price retrieval with valid data
    - [ ] Test error cases with missing prices

- [ ] 3.0 Modify BatchYFinanceQuoteService Implementation
  - [ ] 3.1 Update batch request to include bid/ask prices
    - [ ] Modify data fetching to include 'Low' and 'High' columns
    - [ ] Update caching to store bid/ask prices
  - [ ] 3.2 Implement new bid/ask price methods
    - [ ] Implement `get_bid_price` using 'Low' column
    - [ ] Implement `get_ask_price` using 'High' column
  - [ ] 3.3 Add simple error handling
    - [ ] Raise ValueError with descriptive message if bid/ask prices are missing from DataFrame
  - [ ] 3.4 Update tests
    - [ ] Test bid/ask price retrieval with valid data
    - [ ] Test error cases with missing prices

- [ ] 4.0 Update Holding Class
  - [ ] 4.1 Modify Holding class to support optional bid/ask prices
    - [ ] Update __init__ to accept optional bid_price and ask_price parameters
    - [ ] Default bid_price and ask_price to price if not specified
    - [ ] Update type hints and docstrings
  - [ ] 4.2 Update buy/sell methods to use appropriate prices
    - [ ] Modify `buy` to use ask_price (or price if ask_price not set)
    - [ ] Modify `sell` to use bid_price (or price if bid_price not set)
  - [ ] 4.3 Update from_quote_service class method
    - [ ] Add optional bid/ask price parameters
    - [ ] Update docstring to explain default behavior
  - [ ] 4.4 Update tests
    - [ ] Test Holding creation with and without bid/ask prices
    - [ ] Test buy/sell with default prices (no bid/ask specified)
    - [ ] Test buy/sell with explicit bid/ask prices
    - [ ] Test value calculation still uses main price
    - [ ] Test from_quote_service with and without bid/ask prices

- [ ] 5.0 Add Price Validation and Warning System
  - [ ] 5.1 Implement warning system for price anomalies
    - [ ] Add warning for bid > ask price
    - [ ] Add warning for bid > market price
    - [ ] Add warning for ask < market price
    - [ ] Add warning for spread > 5% of market price
  - [ ] 5.2 Add validation in QuoteService implementations
    - [ ] Add validation in YFinanceQuoteService
    - [ ] Add validation in BatchYFinanceQuoteService
  - [ ] 5.3 Add tests for warning system
    - [ ] Test all warning conditions
    - [ ] Test warning messages

- [ ] 6.0 Update Tests and Documentation
  - [ ] 6.1 Update existing tests
    - [ ] Update any tests affected by interface changes
    - [ ] Add new test cases for bid/ask functionality
  - [ ] 6.2 Add integration tests
    - [ ] Test with actual yfinance data
    - [ ] Test edge cases with real market data
  - [ ] 6.3 Update documentation
    - [ ] Update docstrings for all modified classes/methods
    - [ ] Update any relevant README sections
    - [ ] Add examples of new functionality

## Notes

- All tests should be placed in the `tests/` directory
- Use `unittest` for all tests
- Run all tests with `poetry run python -m unittest discover tests`
- The implementation should maintain backward compatibility where possible
- Warnings should be clear and actionable for users
- Consider adding logging for warnings to help with debugging
- Existing tests should not need significant changes due to backward compatibility
- Any significant changes to existing tests require explicit approval 