"""
Retry Policy Implementation

Automatically retry failed operations with exponential backoff and jitter to
handle transient failures without overwhelming services.

Retry Strategy:
    Attempt 1: immediate
    Attempt 2: base_delay + jitter (e.g., 1s + 0-0.1s)
    Attempt 3: base_delay * 2^1 + jitter (e.g., 2s + 0-0.2s)
    Attempt 4: base_delay * 2^2 + jitter (e.g., 4s + 0-0.4s)
    ...up to max_delay
"""

from functools import wraps
from typing import Callable, Optional, Tuple, Any, Union
import time
import random
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    number: int
    max_attempts: int
    next_delay: float
    exception: Optional[Exception] = None

    @property
    def should_retry(self) -> bool:
        """Check if more retries are available."""
        return self.number < self.max_attempts

    def wait(self) -> None:
        """Wait for next_delay seconds before retry."""
        if self.next_delay > 0:
            logger.debug(f"Waiting {self.next_delay:.2f}s before retry attempt {self.number + 1}")
            time.sleep(self.next_delay)


class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.

    Thread-safe implementation suitable for production use.

    Args:
        max_attempts: Total number of attempts (initial + retries)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Backoff multiplier (typically 2)
        jitter: Whether to add randomness to prevent thundering herd
        retryable_exceptions: Tuple of exception types that trigger retry

    Example:
        >>> retry = RetryPolicy(max_attempts=3, base_delay=1.0)
        >>> @retry.retry
        ... def fetch_data():
        ...     return api.get_data()
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[type, ...] = (Exception,)
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_delay < 0:
            raise ValueError("base_delay must be non-negative")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")

        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * exponential_base^attempt
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.jitter and delay > 0:
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative

        return delay

    def attempts(self) -> 'RetryAttemptIterator':
        """
        Get iterator for manual retry loop.

        Example:
            >>> for attempt in retry_policy.attempts():
            ...     try:
            ...         result = unreliable_operation()
            ...         break
            ...     except RetryableError as e:
            ...         if not attempt.should_retry:
            ...             raise
            ...         logger.info(f"Retry {attempt.number}")
            ...         attempt.wait()
        """
        return RetryAttemptIterator(self)

    def retry(self, func: Callable) -> Callable:
        """
        Decorator for automatic retry on failure.

        Example:
            >>> @retry_policy.retry
            ... def fetch_user_data(user_id):
            ...     return api.get(f"/users/{user_id}")
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt_num in range(self.max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if attempt_num > 0:
                        logger.info(
                            f"Succeeded on attempt {attempt_num + 1}/{self.max_attempts}"
                        )
                    return result

                except self.retryable_exceptions as e:
                    last_exception = e
                    is_last_attempt = (attempt_num + 1 >= self.max_attempts)

                    if is_last_attempt:
                        logger.error(
                            f"Failed after {self.max_attempts} attempts: {e}"
                        )
                        raise

                    delay = self._calculate_delay(attempt_num)
                    logger.warning(
                        f"Attempt {attempt_num + 1}/{self.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

            # Should never reach here, but just in case
            raise last_exception or Exception("Retry logic error")

        return wrapper

    def retry_if(self, condition: Callable[[Any], bool]) -> Callable:
        """
        Decorator that retries based on result condition.

        Args:
            condition: Function that takes result and returns True to retry

        Example:
            >>> @retry_policy.retry_if(lambda r: r.status_code == 429)
            ... def call_rate_limited_api():
            ...     return requests.get(api_url)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_result = None

                for attempt_num in range(self.max_attempts):
                    try:
                        result = func(*args, **kwargs)

                        # Check if we should retry based on result
                        if condition(result):
                            is_last_attempt = (attempt_num + 1 >= self.max_attempts)

                            if is_last_attempt:
                                logger.warning(
                                    f"Retry condition still true after {self.max_attempts} attempts"
                                )
                                return result

                            delay = self._calculate_delay(attempt_num)
                            logger.info(
                                f"Retry condition met on attempt {attempt_num + 1}. "
                                f"Retrying in {delay:.2f}s..."
                            )
                            time.sleep(delay)
                            last_result = result
                            continue

                        # Success - condition not met
                        if attempt_num > 0:
                            logger.info(
                                f"Succeeded on attempt {attempt_num + 1}/{self.max_attempts}"
                            )
                        return result

                    except self.retryable_exceptions as e:
                        is_last_attempt = (attempt_num + 1 >= self.max_attempts)

                        if is_last_attempt:
                            logger.error(f"Failed after {self.max_attempts} attempts: {e}")
                            raise

                        delay = self._calculate_delay(attempt_num)
                        logger.warning(
                            f"Attempt {attempt_num + 1} failed: {e}. Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)

                return last_result

            return wrapper
        return decorator

    def retry_if_exception_type(self, *exception_types: type) -> Callable:
        """
        Decorator that only retries specific exception types.

        Example:
            >>> @retry_policy.retry_if_exception_type(TimeoutError, ConnectionError)
            ... def network_call():
            ...     return api.get_data()
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None

                for attempt_num in range(self.max_attempts):
                    try:
                        result = func(*args, **kwargs)
                        if attempt_num > 0:
                            logger.info(f"Succeeded on attempt {attempt_num + 1}")
                        return result

                    except exception_types as e:
                        last_exception = e
                        is_last_attempt = (attempt_num + 1 >= self.max_attempts)

                        if is_last_attempt:
                            logger.error(f"Failed after {self.max_attempts} attempts: {e}")
                            raise

                        delay = self._calculate_delay(attempt_num)
                        logger.warning(
                            f"Attempt {attempt_num + 1} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)

                raise last_exception or Exception("Retry logic error")

            return wrapper
        return decorator

    def retry_if_result(self, predicate: Callable[[Any], bool]) -> Callable:
        """
        Decorator that retries based on result predicate.

        Example:
            >>> @retry_policy.retry_if_result(lambda r: r['status'] == 'pending')
            ... def poll_job_status(job_id):
            ...     return job_api.get_status(job_id)
        """
        return self.retry_if(predicate)


class RetryAttemptIterator:
    """Iterator for manual retry loop control."""

    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self.attempt_num = 0

    def __iter__(self):
        return self

    def __next__(self) -> RetryAttempt:
        if self.attempt_num >= self.policy.max_attempts:
            raise StopIteration

        delay = self.policy._calculate_delay(self.attempt_num)
        attempt = RetryAttempt(
            number=self.attempt_num,
            max_attempts=self.policy.max_attempts,
            next_delay=delay
        )

        self.attempt_num += 1
        return attempt


# Convenience retry decorators
def retry_on_exception(
    exceptions: Union[type, Tuple[type, ...]] = Exception,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Callable:
    """
    Convenience decorator for retrying on specific exceptions.

    Example:
        >>> @retry_on_exception(ConnectionError, max_attempts=5)
        ... def flaky_network_call():
        ...     return api.get_data()
    """
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    policy = RetryPolicy(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        retryable_exceptions=exceptions
    )
    return policy.retry


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> Callable:
    """
    Convenience decorator for exponential backoff retry.

    Example:
        >>> @retry_with_backoff(max_attempts=5, base_delay=2.0)
        ... def important_operation():
        ...     return perform_critical_task()
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        jitter=jitter
    )
    return policy.retry


# Example usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create retry policy
    retry_policy = RetryPolicy(
        max_attempts=4,
        base_delay=1.0,
        max_delay=10.0,
        retryable_exceptions=(ConnectionError, TimeoutError)
    )

    # Test 1: Decorator with eventual success
    print("Test 1: Eventual success")
    attempt_count = {'count': 0}

    @retry_policy.retry
    def flaky_function():
        attempt_count['count'] += 1
        if attempt_count['count'] < 3:
            raise ConnectionError(f"Temporary failure (attempt {attempt_count['count']})")
        return f"Success on attempt {attempt_count['count']}"

    try:
        result = flaky_function()
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"Failed: {e}\n")

    # Test 2: Manual retry loop
    print("Test 2: Manual retry loop")
    for attempt in retry_policy.attempts():
        try:
            print(f"Attempting operation (attempt {attempt.number + 1})")
            if attempt.number < 2:
                raise TimeoutError("Service timeout")
            print("Success!")
            break
        except TimeoutError as e:
            if not attempt.should_retry:
                print(f"All retries exhausted: {e}")
                break
            print(f"Failed: {e}")
            attempt.wait()

    # Test 3: Conditional retry
    print("\nTest 3: Conditional retry based on result")
    poll_count = {'count': 0}

    @retry_policy.retry_if_result(lambda r: r['status'] == 'pending')
    def poll_status():
        poll_count['count'] += 1
        if poll_count['count'] < 3:
            return {'status': 'pending', 'attempt': poll_count['count']}
        return {'status': 'complete', 'attempt': poll_count['count']}

    result = poll_status()
    print(f"Final result: {result}")
