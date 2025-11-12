---
name: resilience-patterns
description: Implement battle-tested resilience patterns (Circuit Breaker, Retry Logic, Dead Letter Queue, Rate Limiting) for systems with external dependencies. Use when building fault-tolerant microservices, API integrations, message queues, or any system requiring graceful degradation under failure conditions. Essential for production systems with APIs, databases, third-party services, or distributed architectures.
---

# Resilience Patterns

## Overview

Resilience patterns are proven strategies for building fault-tolerant systems that gracefully handle failures, prevent cascading failures, and maintain service availability under adverse conditions. This skill provides production-ready implementations of four critical resilience patterns:

1. **Circuit Breaker** - Prevent cascading failures by detecting and isolating unhealthy services
2. **Retry Logic** - Automatically retry failed operations with exponential backoff
3. **Dead Letter Queue** - Isolate and handle permanently failed messages
4. **Rate Limiting** - Protect services from overload using token bucket algorithm

These patterns are domain-agnostic and can be applied to any system with external dependencies, making them essential building blocks for reliable distributed systems.

## Quick Start

### When to Use Each Pattern

**Circuit Breaker** - Use when:
- Calling external APIs or services that may be unstable
- Protecting downstream services from overload
- Need to fail fast instead of waiting for timeouts
- Want to prevent cascading failures across microservices

**Retry Logic** - Use when:
- Transient failures are expected (network issues, rate limits)
- Operations are idempotent and safe to retry
- Want automatic recovery from temporary failures
- Need exponential backoff to avoid thundering herd

**Dead Letter Queue** - Use when:
- Processing messages/events that may permanently fail
- Need to isolate poison messages from healthy flow
- Want to analyze and manually handle failed operations
- Implementing message-driven architectures

**Rate Limiting** - Use when:
- Protecting APIs from overload or abuse
- Implementing fair usage policies
- Complying with third-party API rate limits
- Need to throttle requests across distributed systems

### Basic Usage Pattern

```python
from scripts.circuit_breaker import CircuitBreaker
from scripts.retry_policy import RetryPolicy
from scripts.rate_limiter import RateLimiter
from scripts.dlq import DeadLetterQueue

# Combine patterns for maximum resilience
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
rate_limiter = RateLimiter(rate=100, per=60)  # 100 requests per 60 seconds
dlq = DeadLetterQueue()

@circuit_breaker.call
@retry_policy.retry
@rate_limiter.limit
def call_external_api(data):
    # Your API call here
    response = external_service.post(data)
    if not response.ok:
        raise ExternalServiceError()
    return response.json()
```

## Core Pattern: Circuit Breaker

### Purpose
Prevent cascading failures by automatically detecting unhealthy services and "opening" the circuit to fail fast, then periodically testing recovery.

### State Machine
```
CLOSED (normal operation)
   ↓ (failure_threshold exceeded)
OPEN (failing fast)
   ↓ (timeout elapsed)
HALF_OPEN (testing recovery)
   ↓ (success) → CLOSED
   ↓ (failure) → OPEN
```

### Implementation

See `scripts/circuit_breaker.py` for full implementation. Key features:

**States:**
- `CLOSED`: Normal operation, requests pass through, failures counted
- `OPEN`: Circuit broken, requests fail immediately without calling service
- `HALF_OPEN`: Testing if service recovered, single test request allowed

**Configuration:**
```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 consecutive failures
    success_threshold=2,      # Close after 2 consecutive successes in HALF_OPEN
    timeout=60,              # Try recovery after 60 seconds
    expected_exceptions=(     # Only count these as failures
        RequestException,
        TimeoutError,
        ConnectionError
    )
)
```

**Usage:**
```python
# Decorator style
@circuit_breaker.call
def call_payment_api():
    return payment_service.process()

# Context manager style
with circuit_breaker:
    result = database.query()

# Direct call style
result = circuit_breaker.call(lambda: api.get_data())
```

**Monitoring:**
```python
# Check circuit state
if circuit_breaker.state == CircuitState.OPEN:
    logger.warning("Payment service circuit is open")

# Get metrics
metrics = circuit_breaker.get_metrics()
# {'state': 'CLOSED', 'failure_count': 2, 'success_count': 150, 'last_failure_time': ...}
```

### Best Practices

1. **Set appropriate thresholds** - Too low causes false positives, too high delays failure detection
2. **Use specific exceptions** - Only count expected failures (not bugs) toward threshold
3. **Monitor state changes** - Alert on state transitions to OPEN
4. **Per-service circuits** - Don't share circuits across different services
5. **Combine with timeouts** - Always set connection/read timeouts on underlying calls

## Core Pattern: Retry Logic

### Purpose
Automatically retry failed operations with exponential backoff and jitter to handle transient failures without overwhelming services.

### Retry Strategy
```
Attempt 1: immediate
Attempt 2: base_delay + jitter (e.g., 1s + 0-0.1s)
Attempt 3: base_delay * 2^1 + jitter (e.g., 2s + 0-0.2s)
Attempt 4: base_delay * 2^2 + jitter (e.g., 4s + 0-0.4s)
...up to max_delay
```

### Implementation

See `scripts/retry_policy.py` for full implementation. Key features:

**Configuration:**
```python
retry_policy = RetryPolicy(
    max_attempts=3,           # Total tries (initial + retries)
    base_delay=1.0,          # Starting delay in seconds
    max_delay=60.0,          # Maximum delay cap
    exponential_base=2,      # Backoff multiplier
    jitter=True,             # Add randomness to prevent thundering herd
    retryable_exceptions=(   # Only retry these exceptions
        TimeoutError,
        ConnectionError,
        TemporaryFailure
    )
)
```

**Usage:**
```python
# Decorator style
@retry_policy.retry
def fetch_user_data(user_id):
    return api.get(f"/users/{user_id}")

# With custom retry condition
@retry_policy.retry_if(lambda result: result.status_code == 429)
def call_rate_limited_api():
    return requests.get(api_url)

# Manual retry
for attempt in retry_policy.attempts():
    try:
        result = unreliable_operation()
        break  # Success, exit retry loop
    except RetryableError as e:
        if not attempt.should_retry:
            raise  # Max attempts reached
        logger.info(f"Attempt {attempt.number} failed, retrying in {attempt.next_delay}s")
        attempt.wait()
```

**Retry Decision Logic:**
```python
# Conditional retry based on exception type
@retry_policy.retry_if_exception_type(TimeoutError, ConnectionError)
def network_call():
    pass

# Conditional retry based on result
@retry_policy.retry_if_result(lambda r: r['status'] == 'pending')
def poll_job_status(job_id):
    return job_api.get_status(job_id)
```

### Best Practices

1. **Ensure idempotency** - Only retry operations that are safe to repeat
2. **Use jitter** - Prevents thundering herd when many clients retry simultaneously
3. **Set max_delay** - Cap exponential backoff to reasonable values (30-60s)
4. **Be selective** - Don't retry client errors (4xx), only transient failures (5xx, network)
5. **Log attempts** - Track retry patterns to identify systemic issues
6. **Combine with Circuit Breaker** - Circuit Breaker should wrap Retry to prevent wasted retries

## Core Pattern: Dead Letter Queue

### Purpose
Isolate permanently failed messages/operations for manual analysis and handling, preventing poison messages from blocking healthy processing.

### Message Lifecycle
```
Message received → Processing attempt → Success ✅
                                     ↓ Failure
                  → Retry attempts → Success ✅
                                     ↓ Permanent failure
                  → Dead Letter Queue → Manual handling
```

### Implementation

See `scripts/dlq.py` for full implementation. Key features:

**Configuration:**
```python
dlq = DeadLetterQueue(
    storage_backend='redis',     # 'memory', 'redis', 'sqs', 'file'
    max_retry_attempts=3,        # Attempts before DLQ
    retention_days=7,            # How long to keep DLQ messages
    alert_threshold=100          # Alert if DLQ size exceeds this
)
```

**Usage:**
```python
# Process with automatic DLQ handling
@dlq.handle_failures
def process_message(message):
    # Your processing logic
    if message.is_invalid():
        raise PermanentFailure("Invalid message format")
    return process(message)

# Manual DLQ operations
try:
    process_message(msg)
except PermanentFailure as e:
    dlq.send(
        message=msg,
        reason=str(e),
        metadata={'source': 'payment_queue', 'user_id': msg.user_id}
    )

# Retrieve and replay DLQ messages
failed_messages = dlq.get_messages(limit=100)
for msg in failed_messages:
    if msg.is_fixable():
        dlq.replay(msg.id)  # Send back to main queue
    else:
        dlq.archive(msg.id)  # Move to long-term storage
```

**Analysis and Monitoring:**
```python
# Get DLQ statistics
stats = dlq.get_stats()
# {
#   'total_messages': 45,
#   'by_reason': {'InvalidFormat': 20, 'TimeoutError': 15, ...},
#   'oldest_message_age': 3600,
#   'messages_last_hour': 5
# }

# Search DLQ
messages = dlq.search(
    reason_contains='ValidationError',
    time_range=(start_time, end_time),
    metadata_filter={'user_id': '12345'}
)

# Bulk operations
dlq.replay_all(reason='TransientError')  # Replay specific failure types
dlq.purge(older_than_days=30)           # Clean up old messages
```

### Best Practices

1. **Separate transient from permanent failures** - Only send permanent failures to DLQ
2. **Include rich metadata** - Store context (user_id, trace_id, timestamp) for debugging
3. **Monitor DLQ size** - Alert when DLQ grows (indicates systemic issues)
4. **Set retention policies** - Don't keep DLQ messages forever
5. **Implement replay mechanism** - Allow manual or automated replay after fixes
6. **Analyze failure patterns** - Regularly review DLQ to identify recurring issues

## Core Pattern: Rate Limiting

### Purpose
Control request rate to prevent service overload, ensure fair usage, and comply with API limits using token bucket algorithm.

### Token Bucket Algorithm
```
Bucket capacity: N tokens
Refill rate: R tokens per T seconds

Request arrives:
  If tokens available:
    Consume 1 token → Allow request
  Else:
    Reject or wait until tokens refilled
```

### Implementation

See `scripts/rate_limiter.py` for full implementation. Key features:

**Configuration:**
```python
# Fixed window rate limiter
rate_limiter = RateLimiter(
    rate=100,                # 100 requests
    per=60,                  # per 60 seconds
    strategy='token_bucket', # 'token_bucket', 'sliding_window', 'fixed_window'
    burst=20                 # Allow burst of 20 above steady rate
)

# Per-user rate limiting
user_limiter = RateLimiter(
    rate=1000,
    per=3600,  # 1000 per hour
    key_func=lambda request: request.user_id  # Separate limit per user
)
```

**Usage:**
```python
# Decorator style (blocks until tokens available)
@rate_limiter.limit
def call_third_party_api():
    return api.get_data()

# Non-blocking check
if rate_limiter.allow(user_id):
    process_request()
else:
    return error_response(429, "Rate limit exceeded")

# Get remaining quota
remaining = rate_limiter.remaining(user_id)
reset_time = rate_limiter.reset_time(user_id)

# Context manager with automatic retry
with rate_limiter.wait_for_token():
    make_api_call()
```

**Advanced Usage:**
```python
# Multi-tier rate limiting
class RateLimitTiers:
    def __init__(self):
        self.free_tier = RateLimiter(rate=100, per=3600)
        self.premium_tier = RateLimiter(rate=1000, per=3600)
        self.enterprise_tier = RateLimiter(rate=10000, per=3600)

    def get_limiter(self, user):
        return getattr(self, f"{user.tier}_tier")

# Distributed rate limiting (Redis-backed)
distributed_limiter = RateLimiter(
    rate=10000,
    per=60,
    backend='redis',
    redis_url='redis://localhost:6379',
    key_prefix='api_rate_limit'
)

# Dynamic rate adjustment
@rate_limiter.limit(rate=lambda: get_current_system_capacity())
def adaptive_handler():
    pass
```

**Monitoring:**
```python
# Get rate limit metrics
metrics = rate_limiter.get_metrics()
# {
#   'requests_allowed': 8543,
#   'requests_rejected': 127,
#   'current_usage': 0.75,  # 75% of capacity
#   'top_consumers': [('user_123', 450), ('user_456', 320), ...]
# }
```

### Best Practices

1. **Choose appropriate granularity** - Per-IP, per-user, per-API-key, or global
2. **Set burst allowance** - Allow short bursts above steady rate for better UX
3. **Return informative headers** - Include X-RateLimit-Remaining, X-RateLimit-Reset
4. **Use distributed limiting** - Redis/Memcached for multi-server deployments
5. **Implement graceful degradation** - Queue or throttle instead of hard reject
6. **Monitor hit rates** - Track how often limits are reached

## Pattern Composition

### Combining Patterns for Maximum Resilience

Patterns are designed to work together and should be composed in specific order:

```python
# Recommended composition order (outermost to innermost):
# 1. Rate Limiter (controls overall throughput)
# 2. Circuit Breaker (fails fast if service unhealthy)
# 3. Retry Logic (handles transient failures)
# 4. Dead Letter Queue (handles permanent failures)

@rate_limiter.limit              # 1. Ensure we don't exceed rate limits
@circuit_breaker.call            # 2. Fail fast if circuit is open
@retry_policy.retry              # 3. Retry transient failures
@dlq.handle_failures            # 4. Send permanent failures to DLQ
def resilient_api_call(data):
    return external_api.post(data)
```

### Example: Payment Processing System

```python
from scripts.circuit_breaker import CircuitBreaker, CircuitState
from scripts.retry_policy import RetryPolicy
from scripts.rate_limiter import RateLimiter
from scripts.dlq import DeadLetterQueue
import logging

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self):
        # Circuit breaker for payment gateway
        self.circuit = CircuitBreaker(
            failure_threshold=5,
            timeout=30,
            expected_exceptions=(PaymentGatewayError, TimeoutError)
        )

        # Retry transient failures (network issues, rate limits)
        self.retry = RetryPolicy(
            max_attempts=3,
            base_delay=2.0,
            max_delay=10.0,
            retryable_exceptions=(TimeoutError, TemporaryFailure)
        )

        # Rate limiter to comply with gateway limits
        self.rate_limiter = RateLimiter(
            rate=100,  # 100 requests per minute
            per=60
        )

        # DLQ for permanently failed payments
        self.dlq = DeadLetterQueue(
            storage_backend='redis',
            retention_days=30,
            alert_threshold=50
        )

    def process_payment(self, payment_request):
        """
        Process payment with full resilience pattern stack.
        """
        # Check circuit state before attempting
        if self.circuit.state == CircuitState.OPEN:
            logger.error("Payment gateway circuit is open, failing fast")
            self.dlq.send(
                message=payment_request,
                reason="Circuit breaker open",
                metadata={'user_id': payment_request.user_id}
            )
            raise ServiceUnavailable("Payment gateway temporarily unavailable")

        # Apply rate limiting
        if not self.rate_limiter.allow(key='payment_gateway'):
            wait_time = self.rate_limiter.reset_time('payment_gateway')
            logger.warning(f"Rate limit reached, waiting {wait_time}s")
            time.sleep(wait_time)

        # Attempt payment with retry and circuit breaker
        try:
            @self.circuit.call
            @self.retry.retry
            def _process():
                return self._call_payment_gateway(payment_request)

            result = _process()
            logger.info(f"Payment processed successfully: {result.transaction_id}")
            return result

        except TemporaryFailure as e:
            # Exhausted retries, send to DLQ for later processing
            logger.error(f"Payment failed after retries: {e}")
            self.dlq.send(
                message=payment_request,
                reason=f"Retry exhausted: {str(e)}",
                metadata={
                    'user_id': payment_request.user_id,
                    'amount': payment_request.amount,
                    'attempts': self.retry.max_attempts
                }
            )
            raise PaymentFailed("Payment processing failed, will be retried later")

        except PermanentFailure as e:
            # Permanent failure (invalid card, insufficient funds)
            logger.error(f"Payment permanently failed: {e}")
            self.dlq.send(
                message=payment_request,
                reason=f"Permanent failure: {str(e)}",
                metadata={'user_id': payment_request.user_id, 'requires_action': True}
            )
            raise

    def _call_payment_gateway(self, request):
        """Actual payment gateway call."""
        response = payment_gateway_client.process(
            card=request.card,
            amount=request.amount,
            currency=request.currency
        )

        if response.status == 'declined':
            raise PermanentFailure(response.decline_reason)
        elif response.status == 'error':
            raise TemporaryFailure(response.error_message)

        return response

    def replay_failed_payments(self):
        """
        Manually replay failed payments from DLQ.
        """
        failed_payments = self.dlq.get_messages(limit=100)
        replayed = 0

        for msg in failed_payments:
            # Only replay transient failures, not permanent ones
            if 'Permanent failure' not in msg.reason:
                try:
                    self.process_payment(msg.message)
                    self.dlq.acknowledge(msg.id)
                    replayed += 1
                except Exception as e:
                    logger.error(f"Replay failed for {msg.id}: {e}")

        logger.info(f"Replayed {replayed}/{len(failed_payments)} failed payments")
        return replayed
```

### Example: Microservice Integration

```python
class UserService:
    """
    Microservice that integrates with multiple external services.
    """
    def __init__(self):
        # Separate circuit breakers per service
        self.auth_circuit = CircuitBreaker(failure_threshold=3, timeout=20)
        self.profile_circuit = CircuitBreaker(failure_threshold=5, timeout=30)
        self.notification_circuit = CircuitBreaker(failure_threshold=10, timeout=60)

        # Shared retry policy
        self.retry = RetryPolicy(max_attempts=3, base_delay=1.0)

        # Per-service rate limiters
        self.auth_limiter = RateLimiter(rate=1000, per=60)
        self.profile_limiter = RateLimiter(rate=500, per=60)
        self.notification_limiter = RateLimiter(rate=200, per=60)

        # Shared DLQ
        self.dlq = DeadLetterQueue(storage_backend='redis')

    @auth_limiter.limit
    @auth_circuit.call
    @retry.retry
    def authenticate_user(self, credentials):
        return auth_service.verify(credentials)

    @profile_limiter.limit
    @profile_circuit.call
    @retry.retry
    def get_user_profile(self, user_id):
        return profile_service.get(user_id)

    @notification_limiter.limit
    @notification_circuit.call
    @dlq.handle_failures  # Notifications can fail permanently
    def send_notification(self, user_id, message):
        return notification_service.send(user_id, message)

    def get_health_status(self):
        """
        Check health of all external dependencies.
        """
        return {
            'auth_service': {
                'circuit_state': self.auth_circuit.state.name,
                'rate_limit_remaining': self.auth_limiter.remaining()
            },
            'profile_service': {
                'circuit_state': self.profile_circuit.state.name,
                'rate_limit_remaining': self.profile_limiter.remaining()
            },
            'notification_service': {
                'circuit_state': self.notification_circuit.state.name,
                'rate_limit_remaining': self.notification_limiter.remaining(),
                'dlq_size': self.dlq.size()
            }
        }
```

## Testing Strategies

### Unit Testing Resilience Patterns

```python
import pytest
import time
from unittest.mock import Mock, patch

class TestCircuitBreaker:
    def test_circuit_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, timeout=60)
        failing_func = Mock(side_effect=Exception("Service down"))

        # Should fail 3 times before opening
        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Next call should fail immediately without calling function
        with pytest.raises(CircuitBreakerOpen):
            cb.call(failing_func)

        assert failing_func.call_count == 3  # Wasn't called 4th time

    def test_circuit_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, timeout=1)
        failing_func = Mock(side_effect=Exception("Error"))

        # Open the circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(1.1)

        # Should transition to HALF_OPEN
        success_func = Mock(return_value="OK")
        result = cb.call(success_func)

        assert result == "OK"
        assert cb.state == CircuitState.CLOSED

class TestRetryPolicy:
    def test_retries_until_success(self):
        rp = RetryPolicy(max_attempts=3, base_delay=0.1)

        # Mock function that fails twice then succeeds
        attempt_count = {'count': 0}
        def flaky_func():
            attempt_count['count'] += 1
            if attempt_count['count'] < 3:
                raise TimeoutError("Temporary failure")
            return "Success"

        result = rp.retry(flaky_func)()

        assert result == "Success"
        assert attempt_count['count'] == 3

    def test_exponential_backoff(self):
        rp = RetryPolicy(max_attempts=4, base_delay=1.0, jitter=False)
        failing_func = Mock(side_effect=TimeoutError)

        start = time.time()
        with pytest.raises(TimeoutError):
            rp.retry(failing_func)()
        duration = time.time() - start

        # Should wait: 0 + 1 + 2 + 4 = 7 seconds (plus execution time)
        assert 7 <= duration < 8

class TestRateLimiter:
    def test_allows_within_limit(self):
        rl = RateLimiter(rate=10, per=1)

        # Should allow 10 requests
        for _ in range(10):
            assert rl.allow() is True

        # 11th should be rejected
        assert rl.allow() is False

    def test_refills_tokens(self):
        rl = RateLimiter(rate=10, per=1)

        # Exhaust tokens
        for _ in range(10):
            rl.allow()

        # Wait for refill
        time.sleep(1.1)

        # Should allow again
        assert rl.allow() is True

class TestDeadLetterQueue:
    def test_sends_to_dlq_on_permanent_failure(self):
        dlq = DeadLetterQueue(storage_backend='memory')

        @dlq.handle_failures
        def failing_func(msg):
            raise PermanentFailure("Invalid message")

        with pytest.raises(PermanentFailure):
            failing_func("test message")

        messages = dlq.get_messages()
        assert len(messages) == 1
        assert messages[0].message == "test message"
```

### Integration Testing

```python
class TestResilientService:
    """
    Integration tests for complete resilient service.
    """
    @pytest.fixture
    def service(self):
        return PaymentProcessor()

    def test_payment_success_path(self, service):
        """Test successful payment processing."""
        request = PaymentRequest(
            user_id="123",
            card="4111111111111111",
            amount=100.00,
            currency="USD"
        )

        result = service.process_payment(request)
        assert result.status == "approved"

    def test_payment_with_transient_failure(self, service):
        """Test payment succeeds after transient failure."""
        with patch.object(payment_gateway_client, 'process') as mock:
            # Fail once, then succeed
            mock.side_effect = [
                TimeoutError("Network timeout"),
                PaymentResponse(status="approved", transaction_id="tx_123")
            ]

            result = service.process_payment(request)
            assert result.status == "approved"
            assert mock.call_count == 2  # Initial + 1 retry

    def test_payment_with_permanent_failure(self, service):
        """Test payment fails and goes to DLQ."""
        with patch.object(payment_gateway_client, 'process') as mock:
            mock.return_value = PaymentResponse(
                status="declined",
                decline_reason="insufficient_funds"
            )

            with pytest.raises(PermanentFailure):
                service.process_payment(request)

            # Should be in DLQ
            dlq_messages = service.dlq.get_messages()
            assert len(dlq_messages) == 1

    def test_circuit_breaker_prevents_calls(self, service):
        """Test circuit breaker opens after failures."""
        with patch.object(payment_gateway_client, 'process') as mock:
            mock.side_effect = PaymentGatewayError("Service unavailable")

            # Trigger circuit breaker
            for _ in range(5):
                try:
                    service.process_payment(request)
                except:
                    pass

            assert service.circuit.state == CircuitState.OPEN

            # Next call should fail immediately
            with pytest.raises(ServiceUnavailable):
                service.process_payment(request)

            # Gateway shouldn't be called when circuit is open
            assert mock.call_count == 5  # Not 6
```

### Chaos Testing

```python
class TestChaosEngineering:
    """
    Chaos testing to validate resilience under adverse conditions.
    """
    def test_network_partition(self, service):
        """Simulate network partition."""
        with chaos.network_partition(service='payment_gateway', duration=30):
            # Service should gracefully degrade
            result = service.process_payment(request)
            assert result.status in ["queued", "failed"]

    def test_dependency_latency(self, service):
        """Inject latency into dependency."""
        with chaos.latency(service='payment_gateway', delay=5.0):
            # Should timeout and retry
            start = time.time()
            service.process_payment(request)
            duration = time.time() - start

            # Should complete faster than 3 * 5s (due to circuit breaker)
            assert duration < 10

    def test_cascading_failures(self, service):
        """Test multiple dependencies failing simultaneously."""
        with chaos.kill_services(['auth', 'profile', 'notification']):
            # Service should isolate failures and continue operating
            health = service.get_health_status()

            # All circuits should be open
            assert health['auth_service']['circuit_state'] == 'OPEN'
            assert health['profile_service']['circuit_state'] == 'OPEN'
            assert health['notification_service']['circuit_state'] == 'OPEN'
```

## Integration with crypto-agent-architect

The resilience-patterns skill integrates seamlessly with crypto-agent-architect for building robust trading systems.

### Example: Resilient Trading Bot

```python
from crypto_agent_architect import TradingAgent
from scripts.circuit_breaker import CircuitBreaker
from scripts.retry_policy import RetryPolicy
from scripts.rate_limiter import RateLimiter
from scripts.dlq import DeadLetterQueue

class ResilientTradingBot(TradingAgent):
    def __init__(self):
        super().__init__()

        # Circuit breakers for exchanges
        self.exchange_circuits = {
            'binance': CircuitBreaker(failure_threshold=5, timeout=60),
            'coinbase': CircuitBreaker(failure_threshold=5, timeout=60),
            'kraken': CircuitBreaker(failure_threshold=5, timeout=60)
        }

        # Retry policy for transient failures
        self.retry = RetryPolicy(
            max_attempts=3,
            base_delay=2.0,
            retryable_exceptions=(NetworkError, RateLimitError)
        )

        # Rate limiters per exchange
        self.rate_limiters = {
            'binance': RateLimiter(rate=1200, per=60),
            'coinbase': RateLimiter(rate=600, per=60),
            'kraken': RateLimiter(rate=300, per=60)
        }

        # DLQ for failed orders
        self.order_dlq = DeadLetterQueue(
            storage_backend='redis',
            retention_days=30
        )

    @rate_limiters['binance'].limit
    @exchange_circuits['binance'].call
    @retry.retry
    def place_order(self, exchange, symbol, side, quantity, price):
        """Place order with full resilience stack."""
        try:
            order = exchange.create_order(
                symbol=symbol,
                type='limit',
                side=side,
                amount=quantity,
                price=price
            )
            return order
        except InsufficientFundsError as e:
            # Permanent failure, send to DLQ
            self.order_dlq.send(
                message={
                    'exchange': exchange.name,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price
                },
                reason=f"Insufficient funds: {e}",
                metadata={'requires_deposit': True}
            )
            raise

    def get_exchange_health(self, exchange_name):
        """Check health of exchange connection."""
        circuit = self.exchange_circuits[exchange_name]
        limiter = self.rate_limiters[exchange_name]

        return {
            'circuit_state': circuit.state.name,
            'rate_limit_remaining': limiter.remaining(),
            'failed_orders_dlq': self.order_dlq.count(
                metadata_filter={'exchange': exchange_name}
            )
        }
```

### Example: Price Oracle with Fallback

```python
class ResilientPriceOracle:
    """
    Multi-source price oracle with automatic fallback.
    """
    def __init__(self):
        self.sources = [
            ('coinmarketcap', self._fetch_cmc),
            ('coingecko', self._fetch_coingecko),
            ('binance', self._fetch_binance)
        ]

        # Circuit breaker per source
        self.circuits = {
            name: CircuitBreaker(failure_threshold=3, timeout=30)
            for name, _ in self.sources
        }

        # Rate limiter per source
        self.rate_limiters = {
            'coinmarketcap': RateLimiter(rate=300, per=60),
            'coingecko': RateLimiter(rate=500, per=60),
            'binance': RateLimiter(rate=1200, per=60)
        }

        self.retry = RetryPolicy(max_attempts=2, base_delay=1.0)

    def get_price(self, symbol):
        """
        Get price with automatic fallback to healthy sources.
        """
        for source_name, fetch_func in self.sources:
            circuit = self.circuits[source_name]
            limiter = self.rate_limiters[source_name]

            # Skip if circuit is open
            if circuit.state == CircuitState.OPEN:
                logger.warning(f"Skipping {source_name} - circuit open")
                continue

            try:
                @limiter.limit
                @circuit.call
                @self.retry.retry
                def _fetch():
                    return fetch_func(symbol)

                price = _fetch()
                logger.info(f"Price from {source_name}: {price}")
                return price

            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
                continue

        raise AllSourcesFailedError("All price sources unavailable")
```

## Advanced Topics

### Distributed Rate Limiting

For multi-server deployments, use Redis-backed rate limiting:

```python
from redis import Redis
from scripts.rate_limiter import DistributedRateLimiter

redis_client = Redis(host='localhost', port=6379)

limiter = DistributedRateLimiter(
    redis_client=redis_client,
    rate=10000,
    per=60,
    key_prefix='api_limit',
    algorithm='sliding_window'  # More accurate than fixed window
)

@limiter.limit(key=lambda req: req.api_key)
def api_handler(request):
    pass
```

### Adaptive Circuit Breaker

Circuit breaker that adapts threshold based on error rate:

```python
from scripts.circuit_breaker import AdaptiveCircuitBreaker

adaptive_cb = AdaptiveCircuitBreaker(
    baseline_failure_threshold=5,
    adaptation_period=300,      # Adjust every 5 minutes
    min_threshold=3,
    max_threshold=20
)

# Automatically adjusts threshold based on observed error rates
```

### Bulkhead Pattern

Isolate resources to prevent cascading failures:

```python
from scripts.bulkhead import Bulkhead

# Limit concurrent calls to protect downstream service
bulkhead = Bulkhead(max_concurrent=10, timeout=5.0)

@bulkhead.isolate
def call_limited_resource():
    return database.query()
```

## Resources

### Implementation Scripts

All pattern implementations are production-ready and fully tested:

- `scripts/circuit_breaker.py` - Circuit Breaker with state machine
- `scripts/retry_policy.py` - Retry logic with exponential backoff
- `scripts/rate_limiter.py` - Token bucket rate limiter
- `scripts/dlq.py` - Dead Letter Queue with multiple backends

### Reference Documentation

- `references/patterns_comparison.md` - Detailed comparison of all patterns with use case matrix
- `references/configuration_guide.md` - Best practices for configuring each pattern

### Further Reading

- [Release It! by Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Stability patterns
- [AWS Architecture Blog - Circuit Breaker](https://aws.amazon.com/builders-library/implementing-health-checks/)
- [Martin Fowler - CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
