# Unit Test Generation Instructions for Asset Allocation

When generating unit tests for this project, adhere to the following principles and structure:

**Framework:** Use the `unittest` framework.

**Location and Naming:**
- Place test files in the `tests/` directory.
- Name test files using the pattern `test_*.py`.

**Testing Principles (Prioritize DAMP over DRY):**
1.  **Keep Cause and Effect Clear:** Arrange all test inputs close to their verification. Keep setup, action, and assertion (Arrange-Act-Assert - AAA pattern) in proximity within the same test method.
2.  **Maintain Test Independence:** Each test should create its own test data rather than relying on complex shared fixtures. Avoid complex `setUp`/`tearDown`.
3.  **Write Explicit Assertions:** Test one behavior per test method. Prefer multiple specific assertions over complex verification logic. Avoid loops or complex logic in the verification section.
4.  **Use Descriptive Test Names:** Name tests to describe the specific behavior being tested. Follow a convention like `test_[feature]_[scenario]_[expected outcome]`.
5.  **Keep Tests Simple:** Tests should be simple enough to inspect manually for correctness. Avoid test helpers that hide important details.
6.  **Structure Tests Logically:** Follow the Arrange-Act-Assert (AAA) pattern. Group test methods by the functionality they test. Use meaningful constants instead of magic values.
