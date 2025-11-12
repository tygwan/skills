---
name: agent-testing-framework
description: Comprehensive testing framework for AI agents with TDD, unit/integration/E2E/chaos testing, LLM mocking, consensus testing, and circuit breaker validation. Use when implementing agent systems, multi-agent architectures, or cryptocurrency trading agents requiring 90%+ unit coverage and 80%+ integration coverage.
---

# Agent Testing Framework

## Overview

Test-driven development framework for AI agent systems with mandatory coverage requirements: 90%+ unit tests, 80%+ integration tests. Includes specialized testing for LLM response mocking, multi-agent consensus, circuit breakers, retry logic, and chaos engineering. Integrates with Playwright for UI testing and Hypothesis for property-based testing.

## When to Use This Skill

**Activation Triggers**:
- Building AI agent systems or multi-agent architectures
- Implementing cryptocurrency trading agents or DeFi automation
- Creating systems with LLM integration requiring reliability testing
- Developing consensus mechanisms or distributed agent coordination
- Need for chaos engineering, load testing, or fault injection
- TDD workflows requiring comprehensive test automation
- Integration with `crypto-agent-architect` testing requirements

**File Type Indicators**: `test_*.py`, `*_test.py`, `conftest.py`, `pytest.ini`, agent architecture files

**Keywords**: "test agent", "TDD", "mock LLM", "consensus testing", "chaos testing", "circuit breaker", "E2E testing"

## Core Testing Philosophy

### Testing Pyramid for Agents

```
           /\
          /  \  Chaos (5%)
         /____\
        /      \  Load Testing (10%)
       /________\
      /          \  E2E Testing (15%)
     /____________\
    /              \  Integration (25%)
   /________________\
  /                  \  Unit Tests (45%)
 /____________________\
```

**Coverage Requirements**:
- **Unit Tests**: 90%+ coverage (agent logic, decision making, state management)
- **Integration Tests**: 80%+ coverage (LLM integration, API calls, multi-agent communication)
- **E2E Tests**: Critical user journeys and trading workflows
- **Load Tests**: Performance under realistic load conditions
- **Chaos Tests**: Resilience to failures and network issues

**TDD Mandatory**: All agent features start with failing tests → implementation → passing tests → refactor cycle.

### Agent-Specific Testing Concerns

1. **LLM Response Mocking**: Deterministic testing with fixture-based LLM responses
2. **Consensus Mechanisms**: Multi-agent agreement validation and failure scenarios
3. **Circuit Breakers**: Failure detection, recovery, and state persistence testing
4. **Retry Logic**: Exponential backoff, jitter, and max retry validation
5. **State Management**: Agent state transitions, persistence, and recovery
6. **Event-Driven Behavior**: Asynchronous event handling and message queuing
7. **Tool Integration**: External API mocking, rate limiting, and error handling
8. **Blockchain Interaction**: Transaction simulation, gas estimation, and revert handling

## Workflow Decision Tree

```
START
  |
  ├─ New Feature? → Write Failing Test → Implement → Pass Test → Refactor
  |
  ├─ Bug Report? → Reproduce with Test → Fix → Verify Test Passes
  |
  ├─ Refactoring? → Ensure Tests Pass → Refactor → Re-run Tests
  |
  ├─ Agent Logic? → Unit Test (mock LLM) → Integration Test (real LLM)
  |
  ├─ Multi-Agent? → Consensus Test → Failure Scenario Test → Load Test
  |
  ├─ Blockchain? → Mock Network → Test Transaction Logic → Integration Test
  |
  └─ Production Ready? → Full Test Suite → Coverage Check → Chaos Test
```

## Test Structure & Organization

### Directory Structure

```
tests/
├── unit/                           # Unit tests (90%+ coverage)
│   ├── test_agent_logic.py        # Agent decision making
│   ├── test_state_management.py   # State transitions
│   ├── test_tool_usage.py         # Tool selection and execution
│   └── test_consensus.py          # Consensus algorithms
├── integration/                    # Integration tests (80%+ coverage)
│   ├── test_llm_integration.py    # LLM API integration
│   ├── test_multi_agent.py        # Multi-agent coordination
│   ├── test_blockchain.py         # Blockchain interaction
│   └── test_external_apis.py      # External service integration
├── e2e/                           # End-to-end tests
│   ├── test_trading_workflow.py   # Complete trading scenarios
│   ├── test_user_journeys.py     # User interaction flows
│   └── test_playwright.py        # UI testing with Playwright
├── load/                          # Load and performance tests
│   ├── test_concurrent_agents.py  # Multi-agent load testing
│   └── test_api_throughput.py    # API performance testing
├── chaos/                         # Chaos engineering tests
│   ├── test_network_failures.py   # Network fault injection
│   ├── test_llm_failures.py      # LLM service failures
│   └── test_circuit_breakers.py  # Circuit breaker activation
├── fixtures/                      # Test fixtures and data
│   ├── llm_responses.json         # Mock LLM responses
│   ├── blockchain_data.json       # Mock blockchain data
│   └── agent_configs.yaml         # Test agent configurations
├── conftest.py                    # Pytest configuration and fixtures
└── pytest.ini                     # Pytest settings
```

### Naming Conventions

- **Test Files**: `test_*.py` or `*_test.py`
- **Test Functions**: `test_<feature>_<scenario>_<expected_outcome>`
- **Test Classes**: `Test<Component>` (e.g., `TestAgentConsensus`)
- **Fixtures**: `<resource>_fixture` or `mock_<service>`

**Examples**:
```python
# Good naming
def test_agent_decision_with_high_confidence_returns_action():
def test_consensus_with_split_vote_triggers_retry():
def test_circuit_breaker_opens_after_threshold_failures():

# Bad naming
def test_agent(): # Too vague
def test_1():     # No context
def test_works(): # No scenario
```

## Unit Testing

### Agent Logic Testing

**Mock LLM responses for deterministic testing**:

```python
import pytest
from unittest.mock import Mock, patch
from agent import TradingAgent

@pytest.fixture
def mock_llm():
    """Mock LLM with predefined responses."""
    mock = Mock()
    mock.generate.return_value = {
        "action": "buy",
        "amount": 1.5,
        "confidence": 0.85,
        "reasoning": "Market trend is bullish"
    }
    return mock

def test_agent_decision_with_high_confidence_returns_buy_action(mock_llm):
    """Test agent makes buy decision with high confidence signals."""
    # Arrange
    agent = TradingAgent(llm=mock_llm)
    market_data = {"price": 45000, "trend": "bullish", "volume": "high"}

    # Act
    decision = agent.make_decision(market_data)

    # Assert
    assert decision["action"] == "buy"
    assert decision["amount"] == 1.5
    assert decision["confidence"] >= 0.8
    mock_llm.generate.assert_called_once()

def test_agent_decision_with_low_confidence_holds_position(mock_llm):
    """Test agent holds position when confidence is below threshold."""
    # Arrange
    mock_llm.generate.return_value = {"action": "hold", "confidence": 0.4}
    agent = TradingAgent(llm=mock_llm, confidence_threshold=0.7)

    # Act
    decision = agent.make_decision({"price": 45000})

    # Assert
    assert decision["action"] == "hold"
    assert decision["confidence"] < 0.7
```

### State Management Testing

```python
def test_agent_state_transitions_from_idle_to_analyzing():
    """Test agent transitions from idle to analyzing state."""
    agent = TradingAgent()
    assert agent.state == "idle"

    agent.start_analysis({"price": 45000})
    assert agent.state == "analyzing"

def test_agent_state_persists_across_restarts():
    """Test agent state is saved and restored."""
    agent = TradingAgent(state_file="test_state.json")
    agent.state = "executing"
    agent.save_state()

    new_agent = TradingAgent(state_file="test_state.json")
    new_agent.load_state()
    assert new_agent.state == "executing"
```

### Tool Usage Testing

```python
def test_agent_selects_correct_tool_for_market_analysis():
    """Test agent selects market analysis tool based on context."""
    agent = TradingAgent()
    tools = agent.select_tools({"task": "analyze_market"})

    assert "market_analyzer" in tools
    assert "sentiment_analyzer" in tools

def test_agent_handles_tool_execution_failure():
    """Test agent handles tool execution failure gracefully."""
    mock_tool = Mock(side_effect=Exception("API error"))
    agent = TradingAgent(tools={"analyzer": mock_tool})

    result = agent.execute_tool("analyzer", {})
    assert result["status"] == "error"
    assert "API error" in result["message"]
```

## Integration Testing

### LLM Integration Testing

```python
@pytest.mark.integration
def test_llm_integration_with_real_api(llm_client):
    """Test agent integrates with real LLM API."""
    agent = TradingAgent(llm=llm_client)
    market_data = {"price": 45000, "trend": "bullish"}

    decision = agent.make_decision(market_data)

    assert "action" in decision
    assert "reasoning" in decision
    assert decision["confidence"] > 0

@pytest.mark.integration
def test_llm_handles_rate_limiting(llm_client):
    """Test agent handles LLM rate limiting with retry logic."""
    agent = TradingAgent(llm=llm_client, max_retries=3)

    # Make multiple rapid requests
    results = [agent.make_decision({"price": 45000}) for _ in range(10)]

    # All requests should eventually succeed
    assert all(r["action"] in ["buy", "sell", "hold"] for r in results)

@pytest.fixture
def llm_client():
    """Fixture for real LLM client (rate-limited for testing)."""
    from llm import OpenAIClient
    return OpenAIClient(api_key="test_key", rate_limit=1)
```

### Multi-Agent Consensus Testing

```python
@pytest.mark.integration
def test_consensus_with_unanimous_agreement_returns_decision():
    """Test multi-agent consensus with unanimous vote."""
    agents = [TradingAgent(id=i) for i in range(5)]
    consensus = ConsensusManager(agents=agents, threshold=0.8)

    # Mock all agents to agree
    for agent in agents:
        agent.make_decision = Mock(return_value={"action": "buy"})

    decision = consensus.reach_consensus({"price": 45000})

    assert decision["action"] == "buy"
    assert decision["confidence"] == 1.0
    assert decision["vote_count"] == 5

@pytest.mark.integration
def test_consensus_with_split_vote_below_threshold_triggers_retry():
    """Test consensus retry mechanism when vote is split."""
    agents = [TradingAgent(id=i) for i in range(5)]
    consensus = ConsensusManager(agents=agents, threshold=0.8, max_retries=3)

    # Mock split vote: 2 buy, 3 sell
    agents[0].make_decision = Mock(return_value={"action": "buy"})
    agents[1].make_decision = Mock(return_value={"action": "buy"})
    agents[2].make_decision = Mock(return_value={"action": "sell"})
    agents[3].make_decision = Mock(return_value={"action": "sell"})
    agents[4].make_decision = Mock(return_value={"action": "sell"})

    decision = consensus.reach_consensus({"price": 45000})

    assert decision["action"] == "sell"  # Majority wins
    assert decision["confidence"] == 0.6  # 3/5
    assert decision["retries"] > 0
```

### Blockchain Integration Testing

```python
@pytest.mark.integration
def test_agent_simulates_transaction_before_execution(mock_blockchain):
    """Test agent simulates blockchain transaction for validation."""
    agent = BlockchainAgent(network=mock_blockchain)

    simulation = agent.simulate_transaction({
        "to": "0x123...",
        "value": 1.5,
        "gas_limit": 21000
    })

    assert simulation["success"] is True
    assert simulation["gas_used"] <= 21000
    assert "estimated_cost" in simulation

@pytest.mark.integration
def test_agent_handles_transaction_revert(mock_blockchain):
    """Test agent handles reverted transactions gracefully."""
    mock_blockchain.send_transaction = Mock(
        side_effect=Exception("Transaction reverted")
    )
    agent = BlockchainAgent(network=mock_blockchain)

    result = agent.execute_transaction({"to": "0x123...", "value": 1.5})

    assert result["status"] == "failed"
    assert "reverted" in result["error"].lower()
```

## E2E Testing with Playwright

### Trading Workflow Testing

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_complete_trading_workflow(page: Page):
    """Test complete trading workflow from login to trade execution."""
    # Login
    page.goto("http://localhost:3000/login")
    page.fill("#email", "test@example.com")
    page.fill("#password", "password123")
    page.click("button[type='submit']")

    # Wait for dashboard
    expect(page).to_have_url("http://localhost:3000/dashboard")

    # Navigate to trading page
    page.click("text=Trade")
    expect(page.locator("h1")).to_contain_text("Trading")

    # Execute trade
    page.select_option("#asset", "BTC")
    page.fill("#amount", "1.5")
    page.click("#buy-button")

    # Verify confirmation
    expect(page.locator(".success-message")).to_be_visible()
    expect(page.locator(".trade-status")).to_contain_text("Completed")

@pytest.mark.e2e
def test_agent_ui_shows_real_time_decisions(page: Page):
    """Test agent UI displays real-time decision updates."""
    page.goto("http://localhost:3000/agent-monitor")

    # Verify initial state
    expect(page.locator(".agent-status")).to_contain_text("Active")

    # Trigger market event (via WebSocket or API)
    page.evaluate("window.triggerMarketUpdate({price: 45000})")

    # Verify agent decision appears
    page.wait_for_selector(".agent-decision", timeout=5000)
    decision = page.locator(".agent-decision").text_content()
    assert decision in ["Buy", "Sell", "Hold"]
```

### Accessibility Testing

```python
@pytest.mark.e2e
def test_trading_interface_meets_wcag_standards(page: Page):
    """Test trading interface accessibility compliance."""
    page.goto("http://localhost:3000/trade")

    # Check keyboard navigation
    page.press("body", "Tab")
    focused = page.locator(":focus")
    assert focused.is_visible()

    # Check ARIA labels
    buy_button = page.locator("#buy-button")
    assert buy_button.get_attribute("aria-label") is not None

    # Check color contrast (using axe-core)
    from axe_playwright_python import Axe
    axe = Axe(page)
    results = axe.run()
    assert len(results.violations) == 0
```

## Circuit Breaker & Retry Testing

### Circuit Breaker Testing

```python
def test_circuit_breaker_opens_after_threshold_failures():
    """Test circuit breaker opens after consecutive failures."""
    mock_service = Mock(side_effect=Exception("Service unavailable"))
    circuit = CircuitBreaker(failure_threshold=3, timeout=60)

    # Trigger failures
    for _ in range(3):
        with pytest.raises(Exception):
            circuit.call(mock_service)

    # Circuit should be open
    assert circuit.state == "open"

    # Further calls should fail fast
    with pytest.raises(CircuitBreakerOpenError):
        circuit.call(mock_service)

def test_circuit_breaker_half_opens_after_timeout():
    """Test circuit breaker transitions to half-open state."""
    mock_service = Mock(side_effect=Exception("Service unavailable"))
    circuit = CircuitBreaker(failure_threshold=2, timeout=1)

    # Trigger circuit open
    for _ in range(2):
        with pytest.raises(Exception):
            circuit.call(mock_service)

    # Wait for timeout
    import time
    time.sleep(1.1)

    # Circuit should be half-open
    assert circuit.state == "half_open"

    # Successful call should close circuit
    mock_service = Mock(return_value="Success")
    result = circuit.call(mock_service)
    assert circuit.state == "closed"

def test_circuit_breaker_persists_state():
    """Test circuit breaker state persists across restarts."""
    circuit = CircuitBreaker(state_file="circuit_state.json")
    circuit.state = "open"
    circuit.save_state()

    new_circuit = CircuitBreaker(state_file="circuit_state.json")
    new_circuit.load_state()
    assert new_circuit.state == "open"
```

### Retry Logic Testing

```python
def test_retry_with_exponential_backoff_succeeds_eventually():
    """Test retry logic with exponential backoff."""
    call_count = 0
    def flaky_service():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "Success"

    result = retry_with_backoff(
        flaky_service,
        max_retries=5,
        base_delay=0.1,
        exponential_base=2
    )

    assert result == "Success"
    assert call_count == 3

def test_retry_adds_jitter_to_prevent_thundering_herd():
    """Test retry logic adds random jitter to backoff delays."""
    delays = []
    def failing_service():
        raise Exception("Failure")

    with pytest.raises(MaxRetriesExceededError):
        retry_with_backoff(
            failing_service,
            max_retries=3,
            base_delay=1.0,
            jitter=True,
            _delay_tracker=delays
        )

    # Delays should not be exact powers of 2
    assert delays[0] != 1.0
    assert delays[1] != 2.0
```

## Load & Performance Testing

### Concurrent Agent Testing

```python
@pytest.mark.load
def test_system_handles_100_concurrent_agents():
    """Test system performance with 100 concurrent agents."""
    import concurrent.futures

    def run_agent(agent_id):
        agent = TradingAgent(id=agent_id)
        return agent.make_decision({"price": 45000})

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(run_agent, i) for i in range(100)]
        results = [f.result() for f in futures]

    # All agents should complete successfully
    assert len(results) == 100
    assert all(r["action"] in ["buy", "sell", "hold"] for r in results)

@pytest.mark.load
def test_api_throughput_meets_requirements():
    """Test API handles required throughput."""
    import time
    start = time.time()

    # Send 1000 requests
    results = []
    for _ in range(1000):
        response = api_client.post("/agent/decision", json={"price": 45000})
        results.append(response.status_code)

    elapsed = time.time() - start
    throughput = 1000 / elapsed

    # Require >100 requests/second
    assert throughput > 100
    assert all(status == 200 for status in results)
```

## Chaos Engineering

### Network Failure Testing

```python
@pytest.mark.chaos
def test_agent_handles_network_partition():
    """Test agent behavior during network partition."""
    agent = TradingAgent()

    # Simulate network partition
    with simulate_network_failure(duration=5):
        decision = agent.make_decision({"price": 45000})

    # Agent should use cached data or default strategy
    assert decision["action"] == "hold"
    assert decision["source"] == "cache"

@pytest.mark.chaos
def test_agent_recovers_after_network_restoration():
    """Test agent resumes normal operation after network recovery."""
    agent = TradingAgent()

    # Simulate network failure and recovery
    with simulate_network_failure(duration=2):
        pass

    # Agent should resume normal operation
    decision = agent.make_decision({"price": 45000})
    assert decision["source"] == "live"
```

### LLM Failure Testing

```python
@pytest.mark.chaos
def test_agent_uses_fallback_when_llm_unavailable():
    """Test agent uses rule-based fallback when LLM fails."""
    mock_llm = Mock(side_effect=Exception("LLM service unavailable"))
    agent = TradingAgent(llm=mock_llm, fallback_strategy="rule_based")

    decision = agent.make_decision({"price": 45000, "trend": "bullish"})

    assert decision["action"] in ["buy", "sell", "hold"]
    assert decision["source"] == "fallback"

@pytest.mark.chaos
def test_circuit_breaker_activates_on_llm_failures():
    """Test circuit breaker prevents cascade failures."""
    mock_llm = Mock(side_effect=Exception("LLM timeout"))
    agent = TradingAgent(llm=mock_llm, circuit_breaker=True)

    # Trigger multiple failures
    for _ in range(5):
        decision = agent.make_decision({"price": 45000})

    # Circuit breaker should be open
    assert agent.circuit_breaker.state == "open"

    # Subsequent calls should fail fast without calling LLM
    decision = agent.make_decision({"price": 45000})
    assert decision["source"] == "circuit_breaker_open"
```

## Property-Based Testing with Hypothesis

### Invariant Testing

```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=1000000))
def test_agent_decision_confidence_always_between_0_and_1(price):
    """Test agent confidence is always valid probability."""
    agent = TradingAgent()
    decision = agent.make_decision({"price": price})

    assert 0 <= decision["confidence"] <= 1

@given(
    st.lists(st.dictionaries(
        keys=st.sampled_from(["action"]),
        values=st.sampled_from(["buy", "sell", "hold"])
    ), min_size=3, max_size=10)
)
def test_consensus_always_returns_majority_vote(decisions):
    """Test consensus always returns majority decision."""
    consensus = ConsensusManager(threshold=0.5)
    result = consensus.aggregate(decisions)

    # Count votes
    votes = {}
    for d in decisions:
        votes[d["action"]] = votes.get(d["action"], 0) + 1

    majority = max(votes, key=votes.get)
    assert result["action"] == majority

@given(st.integers(min_value=0, max_value=10))
def test_retry_logic_never_exceeds_max_retries(max_retries):
    """Test retry logic respects maximum retry limit."""
    call_count = 0
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise Exception("Failure")

    with pytest.raises(MaxRetriesExceededError):
        retry_with_backoff(always_fails, max_retries=max_retries)

    assert call_count <= max_retries + 1  # Initial call + retries
```

## Coverage & Validation

### Running Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=agent --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit -v                    # Unit tests only
pytest tests/integration -v -m integration  # Integration tests
pytest tests/e2e -v -m e2e              # E2E tests
pytest tests/chaos -v -m chaos          # Chaos tests

# Run with coverage thresholds
pytest --cov=agent --cov-fail-under=90  # Fail if <90% coverage
```

### Coverage Validation Script

```python
# scripts/coverage_validator.py
import json
import sys

def validate_coverage(coverage_file="coverage.json", unit_threshold=90, integration_threshold=80):
    """Validate test coverage meets requirements."""
    with open(coverage_file) as f:
        coverage = json.load(f)

    unit_coverage = coverage["totals"]["percent_covered"]
    integration_coverage = coverage["integration"]["percent_covered"]

    print(f"Unit Test Coverage: {unit_coverage}%")
    print(f"Integration Test Coverage: {integration_coverage}%")

    if unit_coverage < unit_threshold:
        print(f"❌ Unit test coverage {unit_coverage}% below threshold {unit_threshold}%")
        sys.exit(1)

    if integration_coverage < integration_threshold:
        print(f"❌ Integration test coverage {integration_coverage}% below threshold {integration_threshold}%")
        sys.exit(1)

    print("✅ All coverage thresholds met")
    sys.exit(0)

if __name__ == "__main__":
    validate_coverage()
```

## Test Automation & CI/CD Integration

### pytest.ini Configuration

```ini
[pytest]
# Test discovery
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (external dependencies)
    e2e: End-to-end tests (full system)
    load: Load and performance tests
    chaos: Chaos engineering tests
    slow: Tests that take >1 second

# Coverage
addopts =
    --cov=agent
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
    --maxfail=3
    --tb=short
    -v

# Timeout
timeout = 300
timeout_method = thread

# Parallel execution
[tool:pytest]
testpaths = tests
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/unit --cov-fail-under=90

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      - run: pytest tests/integration -m integration --cov-fail-under=80

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      - run: playwright install
      - run: pytest tests/e2e -m e2e

  chaos-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      - run: pytest tests/chaos -m chaos
```

## Best Practices

### Test Organization
- **Arrange-Act-Assert**: Structure all tests with clear AAA pattern
- **One Assertion Per Test**: Focus tests on single behavior
- **Descriptive Names**: Test names should describe scenario and expected outcome
- **Independent Tests**: Tests should not depend on execution order
- **Clean Fixtures**: Use pytest fixtures for reusable test setup

### Mocking Strategy
- **Mock External Services**: Always mock LLM APIs, blockchain networks, external APIs
- **Verify Interactions**: Use `assert_called_once()`, `assert_called_with()` for verification
- **Realistic Fixtures**: Mock responses should match real service behavior
- **Deterministic Tests**: Avoid randomness in tests unless testing stochastic behavior

### Performance Considerations
- **Fast Unit Tests**: Unit tests should complete in <100ms
- **Isolated Tests**: Use in-memory databases and mock services
- **Parallel Execution**: Run independent tests in parallel with `pytest-xdist`
- **Skip Slow Tests**: Use `@pytest.mark.slow` and skip in CI with `pytest -m "not slow"`

### Chaos Testing Guidelines
- **Gradual Introduction**: Start with simple failures, increase complexity
- **Production-Like**: Test in staging environment that mirrors production
- **Monitoring**: Always monitor system behavior during chaos tests
- **Rollback Plan**: Have clear rollback procedures before chaos testing

## Resources

### scripts/
- `test_runner.py`: Automated test execution with coverage validation
- `coverage_validator.py`: Coverage threshold enforcement
- `chaos_monkey.py`: Chaos engineering test orchestration

### references/
- `testing_patterns.md`: Comprehensive testing pattern catalog
- `mocking_strategies.md`: LLM and external service mocking strategies
- `playwright_guide.md`: E2E testing with Playwright best practices
- `hypothesis_guide.md`: Property-based testing examples

### Integration with crypto-agent-architect
- Follows `crypto-agent-architect` testing requirements
- Supports multi-agent consensus testing
- Includes blockchain transaction simulation
- Provides circuit breaker and retry logic validation
- Enables chaos engineering for DeFi systems
