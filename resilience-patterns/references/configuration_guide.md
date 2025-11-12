# Resilience Patterns Configuration Guide

Best practices and production-ready configurations for all resilience patterns.

## Configuration Philosophy

### Core Principles

1. **Start Conservative**: Begin with strict limits and relax based on observed behavior
2. **Measure First**: Profile actual failure patterns before optimizing
3. **Environment-Specific**: Development, staging, and production require different configs
4. **Monitor Everything**: Configuration without observability is guesswork
5. **Iterate Based on Data**: Adjust thresholds based on metrics, not intuition

### Configuration Lifecycle

```
Initial Config (conservative)
    ↓
Deploy & Monitor
    ↓
Collect Metrics (1-2 weeks)
    ↓
Analyze Patterns
    ↓
Adjust Configuration
    ↓
A/B Test Changes
    ↓
Gradual Rollout
    ↓
Continue Monitoring
```

## Circuit Breaker Configuration

### Basic Configuration

```python
from scripts.circuit_breaker import CircuitBreaker

# Conservative default
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 consecutive failures
    success_threshold=2,      # Close after 2 consecutive successes in HALF_OPEN
    timeout=60,              # Try recovery after 60 seconds
    expected_exceptions=(
        ConnectionError,
        TimeoutError,
        HTTPError,
        ServiceUnavailableError
    )
)
```

### Environment-Specific Configurations

**Development:**
```python
dev_circuit = CircuitBreaker(
    failure_threshold=10,     # More lenient for unstable dev environments
    success_threshold=1,      # Faster recovery
    timeout=30,              # Shorter timeout for faster iteration
    expected_exceptions=(Exception,)  # Catch all for debugging
)
```

**Staging:**
```python
staging_circuit = CircuitBreaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=45,
    expected_exceptions=(ConnectionError, TimeoutError, HTTPError)
)
```

**Production:**
```python
prod_circuit = CircuitBreaker(
    failure_threshold=3,      # Stricter - fail fast
    success_threshold=3,      # More conservative recovery
    timeout=120,             # Longer timeout - avoid flapping
    expected_exceptions=(
        ConnectionError,
        TimeoutError,
        ReadTimeoutError,
        HTTPError
    ),
    on_state_change=lambda old, new: alert_ops_team(old, new)
)
```

### Service-Type Specific Configurations

**Critical Services (Payment, Auth):**
```python
critical_circuit = CircuitBreaker(
    failure_threshold=2,      # Very strict
    success_threshold=5,      # Very conservative recovery
    timeout=180,             # 3 minutes before retry
    expected_exceptions=(ConnectionError, TimeoutError)
)
```

**Non-Critical Services (Analytics, Logging):**
```python
non_critical_circuit = CircuitBreaker(
    failure_threshold=10,     # More lenient
    success_threshold=2,
    timeout=30,
    expected_exceptions=(Exception,)  # Broader exception handling
)
```

**External APIs (Third-Party):**
```python
external_circuit = CircuitBreaker(
    failure_threshold=5,
    success_threshold=3,
    timeout=300,             # 5 minutes - external services may take longer
    expected_exceptions=(
        RequestException,
        TimeoutError,
        HTTPError
    )
)
```

### Tuning Guidelines

**Failure Threshold Selection:**
- Too low (1-2): Risk of false positives, unnecessary service degradation
- Too high (>10): Slow to detect outages, more wasted requests
- Sweet spot: 3-5 for most services
- Consider: Error rate (e.g., open at >10% error rate over window)

**Timeout Selection:**
- Too short (<30s): Flapping (rapid open/close cycles)
- Too long (>5min): Slow recovery, extended degradation
- Sweet spot: 60-120s for most services
- Consider: MTTR (Mean Time To Recovery) of service

**Success Threshold Selection:**
- Too low (1): Risk of premature closure
- Too high (>5): Slow recovery
- Sweet spot: 2-3 for most services
- Consider: Confidence needed before declaring recovery

## Retry Policy Configuration

### Basic Configuration

```python
from scripts.retry_policy import RetryPolicy

# Conservative default
retry_policy = RetryPolicy(
    max_attempts=3,           # Total tries (initial + 2 retries)
    base_delay=1.0,          # Start with 1 second
    max_delay=60.0,          # Cap at 60 seconds
    exponential_base=2,      # Double each time
    jitter=True,             # Always enable jitter
    retryable_exceptions=(
        TimeoutError,
        ConnectionError,
        TemporaryFailure
    )
)
```

### Environment-Specific Configurations

**Development:**
```python
dev_retry = RetryPolicy(
    max_attempts=2,           # Fail faster for debugging
    base_delay=0.5,
    max_delay=5.0,
    jitter=False             # Predictable timing for debugging
)
```

**Production:**
```python
prod_retry = RetryPolicy(
    max_attempts=5,           # More resilient
    base_delay=2.0,          # Start with longer delay
    max_delay=120.0,         # Higher cap for extreme cases
    exponential_base=2,
    jitter=True
)
```

### Operation-Type Specific Configurations

**Fast Operations (<100ms):**
```python
fast_retry = RetryPolicy(
    max_attempts=3,
    base_delay=0.1,          # Very short initial delay
    max_delay=2.0,           # Low cap
    exponential_base=2,
    jitter=True
)
```

**Network Operations:**
```python
network_retry = RetryPolicy(
    max_attempts=4,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2,
    jitter=True,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        ReadTimeoutError
    )
)
```

**Database Operations:**
```python
db_retry = RetryPolicy(
    max_attempts=3,
    base_delay=0.5,
    max_delay=10.0,
    exponential_base=2,
    jitter=True,
    retryable_exceptions=(
        OperationalError,      # Database connection errors
        DeadlockError,         # Transient deadlocks
        LockTimeoutError
    )
)
```

**External API Calls:**
```python
api_retry = RetryPolicy(
    max_attempts=5,
    base_delay=2.0,
    max_delay=60.0,
    exponential_base=2,
    jitter=True,
    retryable_exceptions=(
        RequestException,
        HTTPError,
        TimeoutError
    )
)
```

### Backoff Strategy Selection

**Exponential Backoff (Standard):**
```
Attempt 1: 0s
Attempt 2: 1s (base_delay)
Attempt 3: 2s (base_delay * 2^1)
Attempt 4: 4s (base_delay * 2^2)
Attempt 5: 8s (base_delay * 2^3)
```

**Linear Backoff (Predictable):**
```python
linear_retry = RetryPolicy(
    max_attempts=5,
    base_delay=2.0,
    exponential_base=1,      # Linear: same delay each time
    jitter=True
)
```

**Aggressive Backoff (Fast failure detection):**
```python
aggressive_retry = RetryPolicy(
    max_attempts=4,
    base_delay=0.5,
    exponential_base=3,      # Triple each time
    max_delay=30.0
)
```

### Tuning Guidelines

**Max Attempts Selection:**
- Too few (1-2): Miss recovery opportunities
- Too many (>5): Waste resources, delay failure notification
- Sweet spot: 3-5 for most operations
- Consider: Total acceptable latency (attempts × avg_delay)

**Base Delay Selection:**
- Too short (<0.5s): May not allow service to recover
- Too long (>5s): Poor user experience
- Sweet spot: 1-2s for most operations
- Consider: Service MTTR and user patience

**Jitter Configuration:**
- Always enable in production
- Prevents thundering herd problem
- Typical range: ±10% of calculated delay

## Rate Limiter Configuration

### Basic Configuration

```python
from scripts.rate_limiter import RateLimiter

# Conservative default
rate_limiter = RateLimiter(
    rate=100,                # 100 requests
    per=60,                  # per 60 seconds
    burst=20,                # Allow 20 additional burst
    strategy='token_bucket'
)
```

### Environment-Specific Configurations

**Development:**
```python
dev_limiter = RateLimiter(
    rate=1000,               # Very high limit
    per=60,
    burst=100,
    strategy='fixed_window'  # Simpler algorithm
)
```

**Production:**
```python
prod_limiter = RateLimiter(
    rate=100,
    per=60,
    burst=10,                # Conservative burst
    strategy='sliding_window'  # More accurate
)
```

### Use-Case Specific Configurations

**API Rate Limiting:**
```python
# Public API
public_api_limiter = RateLimiter(
    rate=1000,               # 1000 requests per hour
    per=3600,
    burst=100,
    key_func=lambda req: req.api_key
)

# Internal API
internal_api_limiter = RateLimiter(
    rate=10000,
    per=3600,
    burst=1000
)
```

**Per-User Rate Limiting:**
```python
user_limiter = RateLimiter(
    rate=100,
    per=60,
    burst=20,
    key_func=lambda req: req.user_id
)
```

**Per-IP Rate Limiting:**
```python
ip_limiter = RateLimiter(
    rate=1000,
    per=3600,
    burst=100,
    key_func=lambda req: req.ip_address
)
```

**Third-Party API Compliance:**
```python
# Stripe API: 100 req/s
stripe_limiter = RateLimiter(
    rate=100,
    per=1,
    burst=10
)

# Twitter API: 300 req/15min
twitter_limiter = RateLimiter(
    rate=300,
    per=900,  # 15 minutes
    burst=0   # No burst for Twitter
)

# GitHub API: 5000 req/hour
github_limiter = RateLimiter(
    rate=5000,
    per=3600,
    burst=100
)
```

### Multi-Tier Rate Limiting

```python
class RateLimitTiers:
    """Different limits for different user tiers."""

    def __init__(self):
        self.tiers = {
            'free': RateLimiter(rate=100, per=3600, burst=10),
            'basic': RateLimiter(rate=1000, per=3600, burst=100),
            'premium': RateLimiter(rate=10000, per=3600, burst=1000),
            'enterprise': RateLimiter(rate=100000, per=3600, burst=10000)
        }

    def get_limiter(self, user):
        return self.tiers.get(user.tier, self.tiers['free'])

    @property
    def limit(self):
        def decorator(func):
            @wraps(func)
            def wrapper(user, *args, **kwargs):
                limiter = self.get_limiter(user)
                if not limiter.allow(key=user.id):
                    raise RateLimitExceeded(f"Rate limit for {user.tier} tier")
                return func(user, *args, **kwargs)
            return wrapper
        return decorator
```

### Distributed Rate Limiting

```python
from redis import Redis
from scripts.rate_limiter import DistributedRateLimiter

redis_client = Redis(
    host='redis.example.com',
    port=6379,
    password='secret',
    db=0,
    socket_connect_timeout=5,
    socket_keepalive=True
)

distributed_limiter = DistributedRateLimiter(
    redis_client=redis_client,
    rate=10000,
    per=60,
    key_prefix='prod_api_limit',
    algorithm='sliding_window'
)
```

### Tuning Guidelines

**Rate Selection:**
- Start with 80% of maximum capacity
- Monitor actual usage and adjust
- Consider: Peak load vs sustained load
- Formula: `rate = max_capacity * 0.8 / expected_replicas`

**Burst Selection:**
- Too low (0): Poor user experience, reject legitimate traffic
- Too high (>50% of rate): Defeats purpose of rate limiting
- Sweet spot: 10-20% of rate
- Consider: User experience vs capacity protection

**Time Window Selection:**
- Short windows (1s-1min): Fine-grained control, more overhead
- Long windows (1hr-1day): Coarse control, less overhead
- Sweet spot: 60s for most APIs
- Consider: User behavior patterns

## Dead Letter Queue Configuration

### Basic Configuration

```python
from scripts.dlq import DeadLetterQueue

# Conservative default
dlq = DeadLetterQueue(
    storage_backend='redis',
    max_retry_attempts=3,
    retention_days=7,
    alert_threshold=100
)
```

### Environment-Specific Configurations

**Development:**
```python
dev_dlq = DeadLetterQueue(
    storage_backend='memory',    # In-memory for dev
    max_retry_attempts=2,
    retention_days=1,
    alert_threshold=10
)
```

**Production:**
```python
prod_dlq = DeadLetterQueue(
    storage_backend='redis',     # Persistent storage
    max_retry_attempts=3,
    retention_days=30,           # Longer retention
    alert_threshold=100,
    storage_config={
        'redis_url': 'redis://prod-redis:6379',
        'key_prefix': 'prod_dlq'
    }
)
```

### Storage Backend Configurations

**In-Memory (Development/Testing):**
```python
memory_dlq = DeadLetterQueue(
    storage_backend='memory',
    retention_days=1
)
```

**File-Based (Single Server):**
```python
file_dlq = DeadLetterQueue(
    storage_backend='file',
    retention_days=7,
    storage_config={
        'file_path': '/var/dlq/messages.json',
        'backup_enabled': True,
        'backup_interval': 3600  # Backup every hour
    }
)
```

**Redis-Based (Distributed):**
```python
redis_dlq = DeadLetterQueue(
    storage_backend='redis',
    retention_days=30,
    storage_config={
        'redis_url': 'redis://redis-cluster:6379',
        'key_prefix': 'dlq',
        'max_message_size': 1024 * 1024,  # 1MB limit
        'compression': True
    }
)
```

**AWS SQS-Based (Cloud):**
```python
sqs_dlq = DeadLetterQueue(
    storage_backend='sqs',
    retention_days=14,  # SQS max
    storage_config={
        'queue_url': 'https://sqs.us-east-1.amazonaws.com/123/dlq',
        'region': 'us-east-1',
        'max_message_size': 262144  # 256KB SQS limit
    }
)
```

### Use-Case Specific Configurations

**Order Processing:**
```python
order_dlq = DeadLetterQueue(
    storage_backend='redis',
    max_retry_attempts=5,        # More retries for orders
    retention_days=90,           # Long retention for audit
    alert_threshold=50,
    storage_config={'key_prefix': 'order_dlq'}
)
```

**Email Notifications:**
```python
email_dlq = DeadLetterQueue(
    storage_backend='file',
    max_retry_attempts=3,
    retention_days=7,            # Shorter retention
    alert_threshold=1000         # Higher threshold (non-critical)
)
```

**Payment Processing:**
```python
payment_dlq = DeadLetterQueue(
    storage_backend='redis',
    max_retry_attempts=3,
    retention_days=365,          # Year-long retention for compliance
    alert_threshold=10,          # Very sensitive (critical)
    storage_config={
        'key_prefix': 'payment_dlq',
        'encryption': True
    }
)
```

### Tuning Guidelines

**Retention Period Selection:**
- Too short (<3 days): Miss recovery opportunities
- Too long (>90 days): Storage costs, stale messages
- Sweet spot: 7-30 days for most use cases
- Consider: Regulatory requirements, SLA commitments

**Alert Threshold Selection:**
- Critical services: 10-50 messages
- Non-critical services: 100-500 messages
- Consider: Normal failure rate, team response time

**Max Retry Attempts:**
- Before DLQ: 3-5 attempts
- Consider: Distinction between transient and permanent failures

## Combined Pattern Configuration

### Complete Resilience Stack

```python
from scripts.circuit_breaker import CircuitBreaker
from scripts.retry_policy import RetryPolicy
from scripts.rate_limiter import RateLimiter
from scripts.dlq import DeadLetterQueue

class ResilientService:
    """Production-ready service with full resilience stack."""

    def __init__(self, service_name: str, tier: str = 'standard'):
        self.service_name = service_name
        self.tier = tier

        # Configuration based on tier
        configs = {
            'critical': {
                'circuit': {'failure_threshold': 2, 'timeout': 180},
                'retry': {'max_attempts': 5, 'base_delay': 2.0},
                'rate': {'rate': 100, 'per': 60, 'burst': 10},
                'dlq': {'retention_days': 90, 'alert_threshold': 10}
            },
            'standard': {
                'circuit': {'failure_threshold': 5, 'timeout': 60},
                'retry': {'max_attempts': 3, 'base_delay': 1.0},
                'rate': {'rate': 1000, 'per': 60, 'burst': 100},
                'dlq': {'retention_days': 30, 'alert_threshold': 100}
            },
            'non_critical': {
                'circuit': {'failure_threshold': 10, 'timeout': 30},
                'retry': {'max_attempts': 2, 'base_delay': 0.5},
                'rate': {'rate': 10000, 'per': 60, 'burst': 1000},
                'dlq': {'retention_days': 7, 'alert_threshold': 1000}
            }
        }

        config = configs[tier]

        # Initialize patterns
        self.circuit = CircuitBreaker(**config['circuit'])
        self.retry = RetryPolicy(**config['retry'])
        self.rate_limiter = RateLimiter(**config['rate'])
        self.dlq = DeadLetterQueue(**config['dlq'])

    def call(self, operation: Callable, *args, **kwargs):
        """Execute operation with full resilience stack."""
        @self.rate_limiter.limit
        @self.circuit.call
        @self.retry.retry
        @self.dlq.handle_failures
        def _execute():
            return operation(*args, **kwargs)

        return _execute()
```

### Usage Examples

```python
# Critical service (payment processing)
payment_service = ResilientService('payment_gateway', tier='critical')

def process_payment(payment_data):
    return payment_service.call(
        gateway.charge,
        payment_data
    )

# Standard service (user API)
user_service = ResilientService('user_api', tier='standard')

def get_user(user_id):
    return user_service.call(
        user_db.get,
        user_id
    )

# Non-critical service (analytics)
analytics_service = ResilientService('analytics', tier='non_critical')

def track_event(event_data):
    return analytics_service.call(
        analytics.send,
        event_data
    )
```

## Monitoring Configuration

### Metrics Collection

```python
import prometheus_client as prom

# Circuit breaker metrics
circuit_state = prom.Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)',
    ['service']
)

circuit_failures = prom.Counter(
    'circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['service']
)

# Retry metrics
retry_attempts = prom.Histogram(
    'retry_attempts',
    'Number of retry attempts before success',
    ['operation']
)

# Rate limiter metrics
rate_limit_rejections = prom.Counter(
    'rate_limit_rejections_total',
    'Total rate limit rejections',
    ['key']
)

# DLQ metrics
dlq_size = prom.Gauge(
    'dlq_size',
    'Current DLQ size',
    ['queue']
)

dlq_age = prom.Gauge(
    'dlq_oldest_message_age_seconds',
    'Age of oldest message in DLQ',
    ['queue']
)
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: resilience_patterns
    rules:
      - alert: CircuitBreakerOpen
        expr: circuit_breaker_state == 2
        for: 5m
        annotations:
          summary: "Circuit breaker open for {{ $labels.service }}"

      - alert: HighRetryRate
        expr: rate(retry_attempts_count[5m]) > 100
        for: 10m
        annotations:
          summary: "High retry rate for {{ $labels.operation }}"

      - alert: RateLimitHitRate
        expr: rate(rate_limit_rejections_total[5m]) / rate(requests_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Rate limit hit rate >10% for {{ $labels.key }}"

      - alert: DLQGrowth
        expr: increase(dlq_size[1h]) > 100
        for: 1h
        annotations:
          summary: "DLQ growing rapidly for {{ $labels.queue }}"
```

## Configuration Validation

### Pre-Deployment Checks

```python
def validate_resilience_config(circuit, retry, rate_limiter, dlq):
    """Validate configuration before deployment."""
    issues = []

    # Circuit breaker validation
    if circuit.failure_threshold < 2:
        issues.append("Circuit failure_threshold too low (<2)")
    if circuit.timeout < 30:
        issues.append("Circuit timeout too short (<30s)")

    # Retry validation
    if retry.max_attempts > 10:
        issues.append("Retry max_attempts too high (>10)")
    total_max_delay = sum(
        retry.base_delay * (retry.exponential_base ** i)
        for i in range(retry.max_attempts)
    )
    if total_max_delay > 300:  # 5 minutes
        issues.append(f"Total retry delay too long ({total_max_delay}s)")

    # Rate limiter validation
    if rate_limiter.burst > rate_limiter.rate:
        issues.append("Rate limiter burst exceeds rate")

    # DLQ validation
    if dlq.retention_days < 1:
        issues.append("DLQ retention too short (<1 day)")

    return issues
```

## Configuration Migration

### Gradual Rollout Strategy

```python
class FeatureFlaggedResilientService:
    """Service with feature-flagged configuration changes."""

    def __init__(self):
        self.flag_client = feature_flags.Client()

        # Old configuration
        self.old_circuit = CircuitBreaker(failure_threshold=10, timeout=60)

        # New configuration
        self.new_circuit = CircuitBreaker(failure_threshold=5, timeout=90)

    def call(self, operation, *args, **kwargs):
        # Use new config for 10% of traffic
        if self.flag_client.is_enabled('new_circuit_config', rollout=0.1):
            circuit = self.new_circuit
        else:
            circuit = self.old_circuit

        return circuit.call(operation, *args, **kwargs)
```

## Troubleshooting Guide

### Common Configuration Issues

**Circuit Breaker Flapping:**
- Symptom: Rapid OPEN ↔ CLOSED transitions
- Cause: Timeout too short, threshold too low
- Fix: Increase timeout to 2-3× MTTR, increase threshold

**Excessive Retries:**
- Symptom: High retry count, slow responses
- Cause: max_attempts too high, no circuit breaker
- Fix: Reduce max_attempts to 3-5, add circuit breaker

**Rate Limit False Positives:**
- Symptom: Legitimate requests rejected
- Cause: Rate too low, no burst allowance
- Fix: Increase rate or burst based on metrics

**DLQ Overflow:**
- Symptom: Storage exhaustion, DLQ never processed
- Cause: Retention too long, no monitoring
- Fix: Reduce retention, implement replay job

## Best Practices Checklist

- [ ] Use environment-specific configurations
- [ ] Start conservative, tune based on metrics
- [ ] Always enable jitter on retry policies
- [ ] Use separate circuit breakers per service
- [ ] Monitor all pattern metrics
- [ ] Set up alerting for critical thresholds
- [ ] Document configuration rationale
- [ ] Review and adjust quarterly
- [ ] Test configuration changes in staging first
- [ ] Use feature flags for gradual rollout
