# Resilience Patterns Comparison

Comprehensive comparison of all four resilience patterns with use case matrix and decision framework.

## Quick Reference Matrix

| Pattern | Primary Goal | When to Use | When NOT to Use | Overhead | Complexity |
|---------|-------------|-------------|-----------------|----------|------------|
| **Circuit Breaker** | Prevent cascading failures | External services may be unstable | Service always reliable | Low | Medium |
| **Retry Logic** | Handle transient failures | Operations are idempotent | Non-idempotent operations | Low | Low |
| **Dead Letter Queue** | Isolate poison messages | Message processing may fail permanently | All failures are transient | Medium | Medium |
| **Rate Limiting** | Prevent overload | Need to control throughput | Unlimited capacity available | Low | Low |

## Detailed Pattern Comparison

### Circuit Breaker vs Retry Logic

**Circuit Breaker:**
- **Purpose**: Fail fast when service is known to be unhealthy
- **Mechanism**: Tracks failure rate, opens circuit after threshold
- **Recovery**: Periodically tests service recovery
- **Best for**: Protecting against sustained outages
- **Metrics**: State changes, failure counts, recovery time

**Retry Logic:**
- **Purpose**: Automatically recover from transient failures
- **Mechanism**: Retries operation with exponential backoff
- **Recovery**: Succeeds when operation works
- **Best for**: Handling temporary network glitches
- **Metrics**: Retry attempts, success rate, backoff timing

**When to combine:**
Always use Circuit Breaker wrapping Retry Logic to prevent wasted retry attempts when service is known to be down.

```python
@circuit_breaker.call    # Outer: fail fast if service down
@retry_policy.retry      # Inner: retry transient failures
def call_service():
    return external_service.get_data()
```

### Dead Letter Queue vs Retry Logic

**Dead Letter Queue:**
- **Purpose**: Handle permanently failed messages
- **Scope**: Message/event processing systems
- **Recovery**: Manual intervention or batch replay
- **Best for**: Isolating poison messages
- **Storage**: Persistent storage required

**Retry Logic:**
- **Purpose**: Handle transient failures automatically
- **Scope**: Any operation that can fail
- **Recovery**: Automatic retry with backoff
- **Best for**: Temporary failures
- **Storage**: No storage required

**When to combine:**
Use Retry Logic first to handle transient failures, then DLQ for permanent failures:

```python
@dlq.handle_failures           # Outer: capture permanent failures
@retry_policy.retry            # Inner: retry transient failures
def process_message(msg):
    if msg.is_permanently_invalid():
        raise PermanentFailure("Invalid format")
    if network_is_flaky():
        raise TemporaryFailure("Network timeout")
    return process(msg)
```

### Rate Limiting vs Circuit Breaker

**Rate Limiting:**
- **Purpose**: Control request throughput
- **Trigger**: Request count threshold
- **Action**: Reject or delay requests
- **Best for**: Protecting service capacity
- **Granularity**: Per-user, per-IP, global

**Circuit Breaker:**
- **Purpose**: Detect and isolate unhealthy services
- **Trigger**: Failure rate threshold
- **Action**: Fail fast without calling service
- **Best for**: Preventing cascading failures
- **Granularity**: Per-service

**When to combine:**
Use Rate Limiter to control throughput to external services, Circuit Breaker to detect when they fail:

```python
@rate_limiter.limit           # Outer: respect API rate limits
@circuit_breaker.call         # Middle: fail fast if service down
@retry_policy.retry           # Inner: retry transient failures
def call_third_party_api():
    return api.get_data()
```

## Use Case Decision Matrix

### E-Commerce Checkout

| Scenario | Pattern | Reason |
|----------|---------|--------|
| Payment gateway calls | Circuit Breaker + Retry + Rate Limit | Handle outages, retry timeouts, respect gateway limits |
| Order processing | DLQ + Retry | Retry transient failures, DLQ for invalid orders |
| Inventory checks | Circuit Breaker + Retry | Fail fast if inventory service down |
| Email notifications | DLQ | Send failures to DLQ for manual retry |

### Microservices Architecture

| Service Interaction | Pattern | Configuration |
|---------------------|---------|---------------|
| Auth service → User DB | Circuit Breaker | failure_threshold=5, timeout=30s |
| API Gateway → Backend services | Rate Limiter + Circuit Breaker | rate=1000/min per service |
| Event processor → Message queue | DLQ + Retry | max_retries=3, DLQ retention=7d |
| Service mesh calls | All patterns | Full resilience stack |

### Trading System

| Component | Pattern | Configuration |
|-----------|---------|---------------|
| Exchange API calls | Rate Limiter + Circuit Breaker + Retry | rate=exchange_limit, failure_threshold=3 |
| Order placement | DLQ + Retry | Retry network failures, DLQ insufficient funds |
| Price oracle | Circuit Breaker with fallback | Multiple sources with independent circuits |
| Market data feed | Circuit Breaker | Fail fast on disconnect |

### Data Pipeline

| Stage | Pattern | Configuration |
|-------|---------|---------------|
| Data ingestion | DLQ + Retry | Retry transient failures, DLQ malformed data |
| Transformation | Retry | max_attempts=5, exponential backoff |
| External API enrichment | Circuit Breaker + Rate Limit + Retry | Full stack with per-API limits |
| Database writes | Retry + Circuit Breaker | Retry deadlocks, circuit for sustained failures |

## Pattern Selection Framework

### Decision Tree

```
1. Is the operation calling an external service?
   YES → Consider Circuit Breaker
   NO → Skip to step 3

2. Does the external service have rate limits?
   YES → Add Rate Limiter
   NO → Continue

3. Can the operation fail transiently?
   YES → Add Retry Logic
   NO → Continue

4. Can the operation fail permanently (poison messages)?
   YES → Add Dead Letter Queue
   NO → Done

5. Combine patterns in recommended order:
   Rate Limiter → Circuit Breaker → Retry Logic → DLQ
```

### Pattern Composition Guidelines

**Order matters!** Apply patterns in this order (outermost to innermost):

1. **Rate Limiter** (outermost)
   - Controls overall throughput
   - Prevents overwhelming downstream services
   - Per-user or global limits

2. **Circuit Breaker** (middle layer)
   - Fails fast if service is known to be unhealthy
   - Prevents wasted retry attempts
   - Per-service circuits

3. **Retry Logic** (inner layer)
   - Handles transient failures automatically
   - Exponential backoff with jitter
   - Operation-specific retry logic

4. **Dead Letter Queue** (innermost)
   - Captures permanently failed operations
   - Enables manual intervention
   - Message/event processing only

## Performance Characteristics

### Latency Impact

| Pattern | Best Case | Worst Case | Average | Notes |
|---------|-----------|------------|---------|-------|
| Circuit Breaker | +0.1ms | +0.1ms | +0.1ms | Minimal overhead, state check only |
| Retry Logic | +0ms | +60s | +2s | Depends on backoff configuration |
| Dead Letter Queue | +1ms | +5ms | +2ms | Storage write overhead |
| Rate Limiter | +0.1ms | +∞ | +0.5ms | Blocking wait if limit exceeded |

### Memory Overhead

| Pattern | Memory Usage | Scalability | Notes |
|---------|--------------|-------------|-------|
| Circuit Breaker | O(1) per instance | Excellent | Fixed state per circuit |
| Retry Logic | O(1) per call | Excellent | No state maintained |
| Dead Letter Queue | O(n) messages | Depends on backend | Grows with failed messages |
| Rate Limiter | O(k) keys | Good | State per rate limit key |

## Failure Mode Analysis

### Circuit Breaker Failure Modes

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| False positive (opens too early) | Unnecessary service degradation | Increase failure_threshold |
| False negative (opens too late) | Cascading failures | Decrease failure_threshold |
| Stuck open | Service never recovers | Monitor state, manual reset |
| Stuck closed | Fails to detect outages | Health check integration |

### Retry Logic Failure Modes

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| Thundering herd | All clients retry simultaneously | Enable jitter |
| Infinite retries | Resource exhaustion | Set max_attempts |
| Non-idempotent retries | Duplicate operations | Ensure idempotency |
| Retry amplification | Overload downstream | Combine with Circuit Breaker |

### Dead Letter Queue Failure Modes

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| DLQ overflow | Storage exhaustion | Set retention policy |
| No monitoring | Failures go unnoticed | Alert on DLQ size |
| Permanent failures retried | Wasted resources | Separate transient/permanent |
| Lost messages | Data loss | Use persistent storage |

### Rate Limiter Failure Modes

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| Clock skew | Incorrect rate calculation | Use token bucket algorithm |
| Distributed inconsistency | Rate limits not enforced | Use Redis/distributed cache |
| Too strict | Legitimate requests rejected | Set burst allowance |
| Too lenient | Service overload | Monitor actual throughput |

## Anti-Patterns

### ❌ Don't: Retry Without Circuit Breaker

```python
# BAD: Wastes resources retrying when service is down
@retry_policy.retry
def call_flaky_service():
    return service.get_data()
```

```python
# GOOD: Circuit breaker prevents wasted retries
@circuit_breaker.call
@retry_policy.retry
def call_flaky_service():
    return service.get_data()
```

### ❌ Don't: Retry Non-Idempotent Operations

```python
# BAD: May create duplicate charges
@retry_policy.retry
def charge_credit_card(amount):
    return payment_gateway.charge(amount)
```

```python
# GOOD: Use idempotency key
@retry_policy.retry
def charge_credit_card(amount, idempotency_key):
    return payment_gateway.charge(amount, idempotency_key)
```

### ❌ Don't: Share Circuit Breaker Across Services

```python
# BAD: One service failure affects all
shared_circuit = CircuitBreaker()

@shared_circuit.call
def call_service_a():
    return service_a.get()

@shared_circuit.call
def call_service_b():
    return service_b.get()
```

```python
# GOOD: Separate circuit per service
circuit_a = CircuitBreaker()
circuit_b = CircuitBreaker()

@circuit_a.call
def call_service_a():
    return service_a.get()

@circuit_b.call
def call_service_b():
    return service_b.get()
```

### ❌ Don't: Ignore DLQ Messages

```python
# BAD: DLQ grows unbounded, failures ignored
dlq = DeadLetterQueue()

@dlq.handle_failures
def process_message(msg):
    # Process and forget about DLQ
    pass
```

```python
# GOOD: Monitor and replay DLQ messages
dlq = DeadLetterQueue(alert_threshold=100)

# Monitor DLQ size
stats = dlq.get_stats()
if stats['total_messages'] > 50:
    alert_operations_team()

# Periodic replay
def replay_dlq_job():
    dlq.replay_all(reason='TransientError', max_age_hours=24)
```

## Real-World Examples

### Example 1: Payment Processing

**Requirements:**
- Handle payment gateway outages gracefully
- Retry transient failures (network timeouts)
- Isolate permanent failures (invalid cards)
- Respect gateway rate limits (100 req/min)

**Solution:**
```python
payment_limiter = RateLimiter(rate=100, per=60)
payment_circuit = CircuitBreaker(failure_threshold=5, timeout=30)
payment_retry = RetryPolicy(max_attempts=3, base_delay=2.0)
payment_dlq = DeadLetterQueue(retention_days=30)

@payment_limiter.limit
@payment_circuit.call
@payment_retry.retry_if_exception_type(TimeoutError, NetworkError)
@payment_dlq.handle_failures
def process_payment(payment):
    if not payment.is_valid():
        raise PermanentFailure("Invalid payment details")
    return gateway.charge(payment)
```

### Example 2: Multi-Source Data Aggregation

**Requirements:**
- Fetch data from multiple sources
- Fail fast if source is unhealthy
- Fallback to other sources
- Cache results to reduce load

**Solution:**
```python
class DataAggregator:
    def __init__(self):
        self.circuits = {
            'source_a': CircuitBreaker(failure_threshold=3, timeout=30),
            'source_b': CircuitBreaker(failure_threshold=3, timeout=30),
            'source_c': CircuitBreaker(failure_threshold=3, timeout=30)
        }
        self.retry = RetryPolicy(max_attempts=2, base_delay=1.0)

    def fetch_data(self, key):
        for source_name, fetch_func in [
            ('source_a', self._fetch_a),
            ('source_b', self._fetch_b),
            ('source_c', self._fetch_c)
        ]:
            circuit = self.circuits[source_name]

            # Skip if circuit is open
            if circuit.state == CircuitState.OPEN:
                continue

            try:
                @circuit.call
                @self.retry.retry
                def _fetch():
                    return fetch_func(key)

                return _fetch()
            except Exception:
                continue

        raise AllSourcesFailedError("All data sources unavailable")
```

### Example 3: Message Queue Processing

**Requirements:**
- Process messages with transient and permanent failures
- Retry transient failures automatically
- Send poison messages to DLQ
- Monitor processing health

**Solution:**
```python
processor_retry = RetryPolicy(
    max_attempts=3,
    retryable_exceptions=(NetworkError, TemporaryFailure)
)
processor_dlq = DeadLetterQueue(
    alert_threshold=100,
    retention_days=7
)

@processor_retry.retry
@processor_dlq.handle_failures
def process_message(message):
    # Validate message
    if not message.is_valid():
        raise PermanentFailure(f"Invalid message format: {message.errors}")

    # Process with potential transient failures
    try:
        result = external_service.process(message)
        return result
    except ServiceUnavailableError:
        raise TemporaryFailure("Service temporarily unavailable")
```

## Monitoring and Observability

### Key Metrics to Track

**Circuit Breaker:**
- State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Time in each state
- Failure rate trends
- Recovery success rate

**Retry Logic:**
- Retry attempt distribution
- Success rate by attempt number
- Total retry cost (time/resources)
- Backoff timing effectiveness

**Dead Letter Queue:**
- DLQ size over time
- Messages by failure reason
- Age of oldest message
- Replay success rate

**Rate Limiter:**
- Request acceptance rate
- Rejection rate by key
- Top consumers
- Burst utilization

### Alerting Strategies

**Critical Alerts:**
- Circuit breaker stuck open >5 minutes
- DLQ size exceeds threshold
- Rate limit rejection rate >10%
- Retry success rate <50%

**Warning Alerts:**
- Circuit breaker state change frequency >10/hour
- DLQ growth rate increasing
- Rate limit approaching capacity
- Retry attempts increasing

## Further Reading

- [Release It! by Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Comprehensive stability patterns
- [AWS Architecture Blog](https://aws.amazon.com/architecture/well-architected/) - Cloud resilience patterns
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) - Site reliability engineering practices
- [Microsoft Azure Architecture](https://docs.microsoft.com/en-us/azure/architecture/patterns/) - Cloud design patterns
