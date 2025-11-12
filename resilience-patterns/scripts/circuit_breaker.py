"""
Circuit Breaker Pattern Implementation

Prevents cascading failures by automatically detecting unhealthy services and
"opening" the circuit to fail fast, then periodically testing recovery.

State Machine:
    CLOSED (normal operation)
       ↓ (failure_threshold exceeded)
    OPEN (failing fast)
       ↓ (timeout elapsed)
    HALF_OPEN (testing recovery)
       ↓ (success) → CLOSED
       ↓ (failure) → OPEN
"""

from enum import Enum
from functools import wraps
from typing import Callable, Optional, Tuple, Any, Dict
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation, requests pass through
    OPEN = "OPEN"          # Circuit broken, fail immediately
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with configurable thresholds and timeout.

    Thread-safe implementation suitable for production use.

    Args:
        failure_threshold: Number of consecutive failures before opening circuit
        success_threshold: Number of consecutive successes in HALF_OPEN before closing
        timeout: Seconds to wait before transitioning from OPEN to HALF_OPEN
        expected_exceptions: Tuple of exception types that count as failures
        on_state_change: Optional callback called when state changes

    Example:
        >>> cb = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> @cb.call
        ... def call_api():
        ...     return api.get_data()
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        expected_exceptions: Tuple[type, ...] = (Exception,),
        on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exceptions = expected_exceptions
        self.on_state_change = on_state_change

        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None

        # Thread safety
        self._lock = threading.RLock()

        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has elapsed to attempt recovery."""
        if self._opened_at is None:
            return False
        elapsed = (datetime.now() - self._opened_at).total_seconds()
        return elapsed >= self.timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state and trigger callback."""
        old_state = self._state
        self._state = new_state

        if new_state == CircuitState.OPEN:
            self._opened_at = datetime.now()
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            logger.info("Circuit breaker closed - service recovered")
        elif new_state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker half-open - testing recovery")

        # Trigger state change callback
        if self.on_state_change and old_state != new_state:
            try:
                self.on_state_change(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")

    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            self._total_calls += 1
            self._total_successes += 1
            self._failure_count = 0  # Reset failure count on success

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)

    def _on_failure(self, exception: Exception) -> None:
        """Handle failed call."""
        with self._lock:
            self._total_calls += 1
            self._total_failures += 1
            self._last_failure_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                # Immediate transition back to OPEN on failure in HALF_OPEN
                self._transition_to(CircuitState.OPEN)
            else:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: If function raises an expected exception
        """
        # Check circuit state
        current_state = self.state
        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpen(
                f"Circuit breaker is open. Service unavailable. "
                f"Will retry after {self.timeout}s timeout."
            )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure(e)
            raise

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator for circuit breaker protection.

        Example:
            >>> @circuit_breaker.call
            ... def api_call():
            ...     return api.get_data()
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

    def __enter__(self):
        """Context manager support."""
        current_state = self.state
        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpen("Circuit breaker is open")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self._on_success()
        elif issubclass(exc_type, self.expected_exceptions):
            self._on_failure(exc_val)
        return False  # Don't suppress exception

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.

        Returns:
            Dictionary with current metrics
        """
        with self._lock:
            return {
                'state': self._state.value,
                'failure_count': self._failure_count,
                'success_count': self._success_count,
                'total_calls': self._total_calls,
                'total_failures': self._total_failures,
                'total_successes': self._total_successes,
                'failure_rate': self._total_failures / max(1, self._total_calls),
                'last_failure_time': self._last_failure_time.isoformat() if self._last_failure_time else None,
                'opened_at': self._opened_at.isoformat() if self._opened_at else None
            }

    def reset(self) -> None:
        """
        Manually reset circuit breaker to CLOSED state.

        Use with caution - typically for administrative purposes only.
        """
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            logger.info("Circuit breaker manually reset")


class AdaptiveCircuitBreaker(CircuitBreaker):
    """
    Circuit breaker that adapts failure threshold based on observed error rates.

    Automatically adjusts sensitivity based on historical patterns.

    Args:
        baseline_failure_threshold: Initial failure threshold
        adaptation_period: Seconds between threshold adjustments
        min_threshold: Minimum allowed threshold
        max_threshold: Maximum allowed threshold

    Example:
        >>> cb = AdaptiveCircuitBreaker(
        ...     baseline_failure_threshold=5,
        ...     adaptation_period=300,
        ...     min_threshold=3,
        ...     max_threshold=20
        ... )
    """

    def __init__(
        self,
        baseline_failure_threshold: int = 5,
        adaptation_period: float = 300.0,
        min_threshold: int = 3,
        max_threshold: int = 20,
        **kwargs
    ):
        super().__init__(failure_threshold=baseline_failure_threshold, **kwargs)
        self.baseline_threshold = baseline_failure_threshold
        self.adaptation_period = adaptation_period
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self._last_adaptation = datetime.now()
        self._window_calls = 0
        self._window_failures = 0

    def _on_success(self) -> None:
        """Track success and adapt threshold."""
        super()._on_success()
        self._window_calls += 1
        self._maybe_adapt_threshold()

    def _on_failure(self, exception: Exception) -> None:
        """Track failure and adapt threshold."""
        super()._on_failure(exception)
        self._window_calls += 1
        self._window_failures += 1
        self._maybe_adapt_threshold()

    def _maybe_adapt_threshold(self) -> None:
        """Adapt threshold based on observed error rate."""
        elapsed = (datetime.now() - self._last_adaptation).total_seconds()
        if elapsed < self.adaptation_period:
            return

        if self._window_calls < 10:  # Need minimum samples
            return

        error_rate = self._window_failures / self._window_calls

        # Adjust threshold based on error rate
        if error_rate > 0.3:  # High error rate - increase sensitivity
            new_threshold = max(self.min_threshold, self.failure_threshold - 1)
        elif error_rate < 0.05:  # Low error rate - decrease sensitivity
            new_threshold = min(self.max_threshold, self.failure_threshold + 1)
        else:
            new_threshold = self.failure_threshold

        if new_threshold != self.failure_threshold:
            logger.info(
                f"Adapting circuit breaker threshold: {self.failure_threshold} → {new_threshold} "
                f"(error_rate={error_rate:.2%})"
            )
            self.failure_threshold = new_threshold

        # Reset window
        self._last_adaptation = datetime.now()
        self._window_calls = 0
        self._window_failures = 0


# Example usage
if __name__ == "__main__":
    import time

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create circuit breaker
    cb = CircuitBreaker(
        failure_threshold=3,
        timeout=5,
        expected_exceptions=(ConnectionError, TimeoutError)
    )

    # Simulate flaky service
    call_count = 0

    def flaky_service():
        global call_count
        call_count += 1
        if call_count <= 3:
            raise ConnectionError(f"Service unavailable (attempt {call_count})")
        return f"Success on attempt {call_count}"

    # Test circuit breaker
    for i in range(8):
        try:
            result = cb.call(flaky_service)
            print(f"Call {i+1}: {result}")
        except (ConnectionError, CircuitBreakerOpen) as e:
            print(f"Call {i+1}: {type(e).__name__}: {e}")

        time.sleep(1)

    # Print metrics
    print("\nMetrics:", cb.get_metrics())
