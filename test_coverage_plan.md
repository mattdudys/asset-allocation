# Test Coverage Analysis and Improvement Plan

## Current Test Coverage

After analyzing the codebase, I've identified the following test coverage:

### Well-Tested Components:
- `asset_class.py` - Comprehensive tests for LeafAssetClass and CompositeAssetClass (test_asset_class.py)
- `holding.py` - Good basic test coverage (test_holdings.py)
- `portfolio.py` - Basic functionality tested (test_portfolio.py)
- `portfolio_loader.py` - Basic loading functionality tested (test_portfolio_loader.py)

### Missing or Insufficient Test Coverage:
1. **Transaction module** (`transaction.py`): No dedicated test file
2. **Snapshot module** (`snapshot.py`): No dedicated test file
3. **Visitor pattern** (`visitor.py`): No dedicated test file
4. **CLI module** (`cli.py`): No tests for command-line functions and argument parsing
5. **QuoteService** (`quote_service.py`): Only indirectly tested via other modules
6. **Portfolio sell_overweight method**: Not explicitly tested
7. **Complex portfolio configurations**: Limited test scenarios with nested asset classes

## Test Improvement Plan

### 1. Transaction Module Tests (`test_transaction.py`)

Create tests for:
- Transaction class creation and properties
- TransactionLog operations (append, iteration)
- TransactionLog.to_dataframe() function
- Empty transaction log behavior

### 2. Snapshot Module Tests (`test_snapshot.py`)

Create tests for:
- AssetClassSnapshot creation and properties
- HoldingSnapshot creation and properties 
- PortfolioSnapshot creation and properties
- PortfolioSnapshotter visitor implementation
- Verify correct information is captured in snapshots

### 3. Visitor Pattern Tests (`test_visitor.py`)

Create tests for:
- Create a custom test visitor implementation
- Verify visitor traversal through hierarchical structures
- Test interaction between visitor and visitable objects

### 4. CLI Module Tests (`test_cli.py`)

Create tests for:
- Argument parsing
- Output formatting functions (print_snapshot, print_transaction_log)
- Command execution functions (invest_excess_cash, sell_overweight)
- End-to-end CLI workflow with mocked components

### 5. QuoteService Tests (`test_quote_service.py`)

Create tests for:
- FakeQuoteService (already partially tested)
- BatchYFinanceQuoteService 
- YFinanceQuoteService (with appropriate mocking)
- Error handling for missing tickers

### 6. Enhanced Portfolio Tests

Extend existing tests to cover:
- Portfolio.sell_overweight() method
- Complex nested asset class hierarchies
- Edge cases (e.g., 0 shares, price changes)
- Rebalancing flows

### 7. Integration Tests

Create test cases that cover:
- End-to-end workflow: load portfolio -> calculate imbalances -> execute trades
- Complex configuration scenarios
- Asset class hierarchy traversal with snapshots

## Implementation Priorities

1. **High Priority**:
   - Transaction module tests (foundational component)
   - Portfolio.sell_overweight() tests (core business logic)
   - Snapshot module tests (critical for output/analysis)

2. **Medium Priority**:
   - Enhanced QuoteService tests
   - Visitor pattern tests
   - Complex portfolio configuration tests

3. **Lower Priority**:
   - CLI module tests (helpful but less critical than core functionality)
   - Integration tests (build after unit tests are solid)

## Implementation Plan

1. Start with creating the high-priority `test_transaction.py` file
2. Implement portfolio.sell_overweight tests (can be added to existing test_portfolio.py)
3. Create `test_snapshot.py` to cover snapshot functionality
4. Progress through medium and lower priority items
5. Use mocking for external dependencies (especially yfinance API)
6. Follow the unit testing guidelines established in CLAUDE.md

Following this plan will significantly improve the test coverage of the project and ensure robustness as the system evolves.