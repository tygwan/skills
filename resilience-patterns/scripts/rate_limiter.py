"""
Rate Limiter Implementation

Control request rate to prevent service overload, ensure fair usage, and comply
with API limits using token bucket algorithm.

Token Bucket Algorithm:
    Bucket capacity: N tokens
    Refill rate: R tokens per T seconds

    Request arrives:
      If tokens available:
        Consume 1 token → Allow request
      Else:
        Reject or wait until tokens refilled
"""

from functools import wraps
from typing import Callable, Optional, Dict, Any
from datetime import datetime, timedelta
import threading
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """
    Token bucket rate limiter implementation.

    Thread-safe implementation suitable for production use.

    Args:
        rate: Number of requests allowed
        per: Time period in seconds
        burst: Additional burst capacity above steady rate
        strategy: Rate limiting strategy ('token_bucket', 'sliding_window', 'fixed_window')
        key_func: Optional function to extract key from request for per-key limiting

    Example:
        >>> limiter = RateLimiter(rate=100, per=60)  # 100 requests per minute
        >>> @limiter.limit
        ... def call_api():
        ...     return api.get_data()
    """

    def __init__(
        self,
        rate: int,
        per: float = 1.0,
        burst: int = 0,
        strategy: str = 'token_bucket',
        key_func: Optional[Callable] = None
    ):
        if rate <= 0:
            raise ValueError("rate must be positive")
        if per <= 0:
            raise ValueError("per must be positive")

        self.rate = rate
        self.per = per
        self.burst = burst
        self.strategy = strategy
        self.key_func = key_func

        # Token bucket parameters
        self.capacity = rate + burst
        self.refill_rate = rate / per  # tokens per second

        # State tracking per key
        self._buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

        # Metrics
        self._total_requests = 0
        self._total_allowed = 0
        self._total_rejected = 0

    def _get_bucket(self, key: str = 'default') -> Dict[str, Any]:
        """Get or create bucket for key."""
        if key not in self._buckets:
            self._buckets[key] = {
                'tokens': self.capacity,
                'last_update': time.time(),
                'requests': 0,
                'allowed': 0,
                'rejected': 0
            }
        return self._buckets[key]

    def _refill_tokens(self, bucket: Dict[str, Any]) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket['last_update']

        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now

    def allow(self, key: str = 'default', tokens: int = 1) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Rate limit key (e.g., user_id, ip_address)
            tokens: Number of tokens to consume (default 1)

        Returns:
            True if allowed, False if rate limit exceeded
        """
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill_tokens(bucket)

            # Track metrics
            self._total_requests += 1
            bucket['requests'] += 1

            # Check if tokens available
            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                self._total_allowed += 1
                bucket['allowed'] += 1
                return True
            else:
                self._total_rejected += 1
                bucket['rejected'] += 1
                logger.debug(
                    f"Rate limit exceeded for key '{key}'. "
                    f"Tokens available: {bucket['tokens']:.2f}/{self.capacity}"
                )
                return False

    def wait_for_token(self, key: str = 'default', tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Wait for tokens to become available.

        Args:
            key: Rate limit key
            tokens: Number of tokens needed
            timeout: Maximum time to wait in seconds (None = no timeout)

        Returns:
            True if tokens acquired, False if timeout

        Raises:
            TimeoutError: If timeout exceeded
        """
        start_time = time.time()

        while True:
            if self.allow(key, tokens):
                return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise TimeoutError(f"Rate limiter timeout after {timeout}s")

            # Calculate wait time
            with self._lock:
                bucket = self._get_bucket(key)
                tokens_needed = tokens - bucket['tokens']
                wait_time = tokens_needed / self.refill_rate

            # Wait a bit before retrying
            time.sleep(min(wait_time, 0.1))

    def remaining(self, key: str = 'default') -> int:
        """
        Get remaining tokens for key.

        Args:
            key: Rate limit key

        Returns:
            Number of tokens remaining
        """
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill_tokens(bucket)
            return int(bucket['tokens'])

    def reset_time(self, key: str = 'default') -> float:
        """
        Get time in seconds until bucket is fully refilled.

        Args:
            key: Rate limit key

        Returns:
            Seconds until full refill
        """
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill_tokens(bucket)
            tokens_to_refill = self.capacity - bucket['tokens']
            return tokens_to_refill / self.refill_rate if tokens_to_refill > 0 else 0

    def limit(self, func: Callable = None, *, blocking: bool = True) -> Callable:
        """
        Decorator for rate limiting.

        Args:
            func: Function to decorate
            blocking: If True, wait for tokens; if False, raise RateLimitExceeded

        Example:
            >>> @limiter.limit
            ... def call_api():
            ...     return api.get_data()

            >>> @limiter.limit(blocking=False)
            ... def non_blocking_call():
            ...     return api.get_data()
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Extract key if key_func provided
                key = 'default'
                if self.key_func:
                    try:
                        key = str(self.key_func(*args, **kwargs))
                    except Exception as e:
                        logger.warning(f"Error extracting rate limit key: {e}")

                # Check/wait for rate limit
                if blocking:
                    self.wait_for_token(key)
                else:
                    if not self.allow(key):
                        raise RateLimitExceeded(
                            f"Rate limit exceeded for key '{key}'. "
                            f"Limit: {self.rate} per {self.per}s. "
                            f"Reset in {self.reset_time(key):.2f}s"
                        )

                return f(*args, **kwargs)
            return wrapper

        # Support both @limiter.limit and @limiter.limit()
        if func is None:
            return decorator
        return decorator(func)

    def __call__(self, func: Callable) -> Callable:
        """Allow using limiter as decorator directly."""
        return self.limit(func)

    def get_metrics(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limiter metrics.

        Args:
            key: Optional specific key to get metrics for

        Returns:
            Dictionary with metrics
        """
        with self._lock:
            if key:
                bucket = self._get_bucket(key)
                return {
                    'key': key,
                    'tokens': bucket['tokens'],
                    'capacity': self.capacity,
                    'requests': bucket['requests'],
                    'allowed': bucket['allowed'],
                    'rejected': bucket['rejected'],
                    'reset_time': self.reset_time(key)
                }
            else:
                # Global metrics
                return {
                    'total_requests': self._total_requests,
                    'total_allowed': self._total_allowed,
                    'total_rejected': self._total_rejected,
                    'rejection_rate': self._total_rejected / max(1, self._total_requests),
                    'active_keys': len(self._buckets),
                    'top_consumers': self._get_top_consumers()
                }

    def _get_top_consumers(self, limit: int = 10) -> list:
        """Get top consumers by request count."""
        consumers = [
            (key, bucket['requests'])
            for key, bucket in self._buckets.items()
        ]
        consumers.sort(key=lambda x: x[1], reverse=True)
        return consumers[:limit]

    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset rate limiter state.

        Args:
            key: If provided, reset specific key; otherwise reset all
        """
        with self._lock:
            if key:
                if key in self._buckets:
                    del self._buckets[key]
                    logger.info(f"Reset rate limiter for key '{key}'")
            else:
                self._buckets.clear()
                self._total_requests = 0
                self._total_allowed = 0
                self._total_rejected = 0
                logger.info("Reset all rate limiter state")


class DistributedRateLimiter:
    """
    Redis-backed distributed rate limiter for multi-server deployments.

    Requires redis-py package: pip install redis

    Args:
        redis_client: Redis client instance
        rate: Number of requests allowed
        per: Time period in seconds
        key_prefix: Prefix for Redis keys
        algorithm: 'token_bucket' or 'sliding_window'

    Example:
        >>> import redis
        >>> redis_client = redis.Redis(host='localhost', port=6379)
        >>> limiter = DistributedRateLimiter(redis_client, rate=1000, per=60)
        >>> @limiter.limit
        ... def api_handler(request):
        ...     return process_request(request)
    """

    def __init__(
        self,
        redis_client: Any,
        rate: int,
        per: float = 1.0,
        key_prefix: str = 'rate_limit',
        algorithm: str = 'sliding_window'
    ):
        self.redis = redis_client
        self.rate = rate
        self.per = per
        self.key_prefix = key_prefix
        self.algorithm = algorithm

    def _get_redis_key(self, key: str) -> str:
        """Get Redis key with prefix."""
        return f"{self.key_prefix}:{key}"

    def allow(self, key: str = 'default') -> bool:
        """
        Check if request is allowed using sliding window algorithm.

        Args:
            key: Rate limit key

        Returns:
            True if allowed, False if rate limit exceeded
        """
        redis_key = self._get_redis_key(key)
        now = time.time()
        window_start = now - self.per

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(redis_key, '-inf', window_start)

        # Count requests in current window
        pipe.zcard(redis_key)

        # Add current request
        pipe.zadd(redis_key, {str(now): now})

        # Set expiry
        pipe.expire(redis_key, int(self.per) + 1)

        results = pipe.execute()
        request_count = results[1]

        # Check if under limit
        return request_count < self.rate

    def limit(self, key_func: Optional[Callable] = None) -> Callable:
        """
        Decorator for distributed rate limiting.

        Args:
            key_func: Function to extract key from request

        Example:
            >>> @limiter.limit(key_func=lambda req: req.user_id)
            ... def api_handler(request):
            ...     return process_request(request)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract key
                key = 'default'
                if key_func:
                    try:
                        key = str(key_func(*args, **kwargs))
                    except Exception as e:
                        logger.warning(f"Error extracting rate limit key: {e}")

                # Check rate limit
                if not self.allow(key):
                    raise RateLimitExceeded(
                        f"Rate limit exceeded for key '{key}'. "
                        f"Limit: {self.rate} per {self.per}s"
                    )

                return func(*args, **kwargs)
            return wrapper
        return decorator


# Example usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create rate limiter: 5 requests per 10 seconds
    limiter = RateLimiter(rate=5, per=10, burst=2)

    # Test 1: Simple rate limiting
    print("Test 1: Simple rate limiting")

    @limiter.limit
    def api_call(user_id: str):
        return f"Processing request for user {user_id}"

    # Make requests
    for i in range(8):
        try:
            result = api_call(f"user_{i}")
            print(f"Request {i+1}: {result}")
            print(f"  Remaining: {limiter.remaining()}")
        except RateLimitExceeded as e:
            print(f"Request {i+1}: Rate limit exceeded")

    # Test 2: Per-user rate limiting
    print("\nTest 2: Per-user rate limiting")
    user_limiter = RateLimiter(
        rate=3,
        per=5,
        key_func=lambda user_id: user_id
    )

    @user_limiter.limit(blocking=False)
    def user_api_call(user_id: str):
        return f"Processing request for {user_id}"

    users = ['alice', 'bob', 'alice', 'alice', 'bob']
    for i, user in enumerate(users):
        try:
            result = user_api_call(user)
            print(f"Request {i+1} ({user}): Success - {limiter.remaining(user)} remaining")
        except RateLimitExceeded:
            print(f"Request {i+1} ({user}): Rate limited")

    # Test 3: Metrics
    print("\nTest 3: Metrics")
    metrics = limiter.get_metrics()
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Total allowed: {metrics['total_allowed']}")
    print(f"Total rejected: {metrics['total_rejected']}")
    print(f"Rejection rate: {metrics['rejection_rate']:.2%}")
