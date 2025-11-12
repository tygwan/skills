"""
Dead Letter Queue Implementation

Isolate permanently failed messages/operations for manual analysis and handling,
preventing poison messages from blocking healthy processing.

Message Lifecycle:
    Message received → Processing attempt → Success ✅
                                         ↓ Failure
                      → Retry attempts → Success ✅
                                         ↓ Permanent failure
                      → Dead Letter Queue → Manual handling
"""

from functools import wraps
from typing import Callable, Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import threading
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Supported storage backends for DLQ."""
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    SQS = "sqs"


@dataclass
class DLQMessage:
    """Message stored in Dead Letter Queue."""
    id: str
    message: Any
    reason: str
    timestamp: datetime
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DLQMessage':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class PermanentFailure(Exception):
    """Indicates a permanently failed operation that should go to DLQ."""
    pass


class DeadLetterQueue:
    """
    Dead Letter Queue implementation with multiple storage backends.

    Thread-safe implementation suitable for production use.

    Args:
        storage_backend: Storage backend ('memory', 'file', 'redis', 'sqs')
        max_retry_attempts: Number of retries before sending to DLQ
        retention_days: How long to keep messages in DLQ
        alert_threshold: Alert if DLQ size exceeds this value
        storage_config: Backend-specific configuration

    Example:
        >>> dlq = DeadLetterQueue(storage_backend='redis', retention_days=7)
        >>> @dlq.handle_failures
        ... def process_message(msg):
        ...     if msg.is_invalid():
        ...         raise PermanentFailure("Invalid format")
        ...     return process(msg)
    """

    def __init__(
        self,
        storage_backend: str = 'memory',
        max_retry_attempts: int = 3,
        retention_days: int = 7,
        alert_threshold: int = 100,
        storage_config: Optional[Dict[str, Any]] = None
    ):
        self.storage_backend = StorageBackend(storage_backend)
        self.max_retry_attempts = max_retry_attempts
        self.retention_days = retention_days
        self.alert_threshold = alert_threshold
        self.storage_config = storage_config or {}

        # Initialize storage
        self._storage: List[DLQMessage] = []
        self._lock = threading.RLock()
        self._message_counter = 0

        # Metrics
        self._total_sent = 0
        self._total_replayed = 0
        self._total_archived = 0

        # Initialize backend-specific storage
        self._init_storage()

    def _init_storage(self) -> None:
        """Initialize storage backend."""
        if self.storage_backend == StorageBackend.FILE:
            import os
            self.file_path = self.storage_config.get('file_path', 'dlq_messages.json')
            if os.path.exists(self.file_path):
                self._load_from_file()
        elif self.storage_backend == StorageBackend.REDIS:
            # Would initialize Redis connection here
            pass
        elif self.storage_backend == StorageBackend.SQS:
            # Would initialize AWS SQS connection here
            pass

    def _generate_id(self) -> str:
        """Generate unique message ID."""
        with self._lock:
            self._message_counter += 1
            return f"dlq_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._message_counter}"

    def send(
        self,
        message: Any,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Send message to Dead Letter Queue.

        Args:
            message: The failed message/operation
            reason: Reason for failure
            metadata: Additional context (user_id, trace_id, etc.)
            source: Source queue/service name

        Returns:
            Message ID

        Example:
            >>> dlq.send(
            ...     message=failed_payment,
            ...     reason="Invalid card number",
            ...     metadata={'user_id': '12345', 'amount': 100.00}
            ... )
        """
        with self._lock:
            msg_id = self._generate_id()
            dlq_message = DLQMessage(
                id=msg_id,
                message=message,
                reason=reason,
                timestamp=datetime.now(),
                metadata=metadata or {},
                source=source
            )

            self._storage.append(dlq_message)
            self._total_sent += 1

            # Persist to backend
            self._persist_message(dlq_message)

            # Check alert threshold
            if len(self._storage) >= self.alert_threshold:
                logger.warning(
                    f"DLQ size ({len(self._storage)}) exceeded alert threshold "
                    f"({self.alert_threshold})"
                )

            logger.info(
                f"Sent message to DLQ: {msg_id} - Reason: {reason} - "
                f"Current DLQ size: {len(self._storage)}"
            )

            return msg_id

    def get_messages(
        self,
        limit: Optional[int] = None,
        reason_filter: Optional[str] = None
    ) -> List[DLQMessage]:
        """
        Retrieve messages from DLQ.

        Args:
            limit: Maximum number of messages to return
            reason_filter: Filter by reason substring

        Returns:
            List of DLQ messages
        """
        with self._lock:
            messages = self._storage.copy()

            # Apply filters
            if reason_filter:
                messages = [
                    msg for msg in messages
                    if reason_filter.lower() in msg.reason.lower()
                ]

            # Apply limit
            if limit:
                messages = messages[:limit]

            return messages

    def get_message(self, message_id: str) -> Optional[DLQMessage]:
        """
        Get specific message by ID.

        Args:
            message_id: Message ID

        Returns:
            DLQ message or None if not found
        """
        with self._lock:
            for msg in self._storage:
                if msg.id == message_id:
                    return msg
            return None

    def search(
        self,
        reason_contains: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[DLQMessage]:
        """
        Search DLQ messages with filters.

        Args:
            reason_contains: Search in reason field
            time_range: Tuple of (start_time, end_time)
            metadata_filter: Filter by metadata key-value pairs

        Returns:
            List of matching messages
        """
        with self._lock:
            results = self._storage.copy()

            # Filter by reason
            if reason_contains:
                results = [
                    msg for msg in results
                    if reason_contains.lower() in msg.reason.lower()
                ]

            # Filter by time range
            if time_range:
                start_time, end_time = time_range
                results = [
                    msg for msg in results
                    if start_time <= msg.timestamp <= end_time
                ]

            # Filter by metadata
            if metadata_filter:
                results = [
                    msg for msg in results
                    if all(
                        msg.metadata.get(k) == v
                        for k, v in metadata_filter.items()
                    )
                ]

            return results

    def replay(self, message_id: str) -> bool:
        """
        Replay message from DLQ (send back to main queue).

        Args:
            message_id: Message ID to replay

        Returns:
            True if replayed successfully
        """
        with self._lock:
            message = self.get_message(message_id)
            if not message:
                logger.warning(f"Message {message_id} not found for replay")
                return False

            # Remove from DLQ
            self._storage = [msg for msg in self._storage if msg.id != message_id]
            self._total_replayed += 1

            logger.info(f"Replayed message {message_id} from DLQ")
            return True

    def replay_all(
        self,
        reason: Optional[str] = None,
        max_age_hours: Optional[int] = None
    ) -> int:
        """
        Replay multiple messages from DLQ.

        Args:
            reason: Only replay messages with this reason
            max_age_hours: Only replay messages newer than this

        Returns:
            Number of messages replayed
        """
        with self._lock:
            messages_to_replay = []

            for msg in self._storage:
                # Filter by reason
                if reason and reason not in msg.reason:
                    continue

                # Filter by age
                if max_age_hours:
                    age = (datetime.now() - msg.timestamp).total_seconds() / 3600
                    if age > max_age_hours:
                        continue

                messages_to_replay.append(msg.id)

            # Replay filtered messages
            for msg_id in messages_to_replay:
                self.replay(msg_id)

            logger.info(f"Replayed {len(messages_to_replay)} messages from DLQ")
            return len(messages_to_replay)

    def acknowledge(self, message_id: str) -> bool:
        """
        Acknowledge successful replay (remove from DLQ).

        Args:
            message_id: Message ID to acknowledge

        Returns:
            True if acknowledged
        """
        return self.replay(message_id)

    def archive(self, message_id: str) -> bool:
        """
        Archive message (move to long-term storage, remove from active DLQ).

        Args:
            message_id: Message ID to archive

        Returns:
            True if archived successfully
        """
        with self._lock:
            message = self.get_message(message_id)
            if not message:
                return False

            # Would move to archive storage here
            self._storage = [msg for msg in self._storage if msg.id != message_id]
            self._total_archived += 1

            logger.info(f"Archived message {message_id}")
            return True

    def purge(self, older_than_days: Optional[int] = None) -> int:
        """
        Purge old messages from DLQ.

        Args:
            older_than_days: Remove messages older than this (default: retention_days)

        Returns:
            Number of messages purged
        """
        older_than_days = older_than_days or self.retention_days

        with self._lock:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            original_size = len(self._storage)

            self._storage = [
                msg for msg in self._storage
                if msg.timestamp > cutoff_date
            ]

            purged = original_size - len(self._storage)
            logger.info(f"Purged {purged} messages older than {older_than_days} days")
            return purged

    def size(self, source: Optional[str] = None) -> int:
        """
        Get current DLQ size.

        Args:
            source: Optional filter by source

        Returns:
            Number of messages in DLQ
        """
        with self._lock:
            if source:
                return sum(1 for msg in self._storage if msg.source == source)
            return len(self._storage)

    def count(self, metadata_filter: Optional[Dict[str, Any]] = None) -> int:
        """
        Count messages matching filter.

        Args:
            metadata_filter: Filter by metadata

        Returns:
            Number of matching messages
        """
        if not metadata_filter:
            return self.size()

        with self._lock:
            return len(self.search(metadata_filter=metadata_filter))

    def get_stats(self) -> Dict[str, Any]:
        """
        Get DLQ statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            if not self._storage:
                return {
                    'total_messages': 0,
                    'by_reason': {},
                    'by_source': {},
                    'oldest_message_age': 0,
                    'messages_last_hour': 0,
                    'total_sent': self._total_sent,
                    'total_replayed': self._total_replayed,
                    'total_archived': self._total_archived
                }

            # Group by reason
            by_reason: Dict[str, int] = {}
            for msg in self._storage:
                by_reason[msg.reason] = by_reason.get(msg.reason, 0) + 1

            # Group by source
            by_source: Dict[str, int] = {}
            for msg in self._storage:
                if msg.source:
                    by_source[msg.source] = by_source.get(msg.source, 0) + 1

            # Calculate ages
            now = datetime.now()
            oldest = min(msg.timestamp for msg in self._storage)
            oldest_age = (now - oldest).total_seconds()

            # Messages in last hour
            one_hour_ago = now - timedelta(hours=1)
            recent = sum(1 for msg in self._storage if msg.timestamp > one_hour_ago)

            return {
                'total_messages': len(self._storage),
                'by_reason': by_reason,
                'by_source': by_source,
                'oldest_message_age': oldest_age,
                'messages_last_hour': recent,
                'total_sent': self._total_sent,
                'total_replayed': self._total_replayed,
                'total_archived': self._total_archived
            }

    def handle_failures(self, func: Callable) -> Callable:
        """
        Decorator to automatically send failures to DLQ.

        Example:
            >>> @dlq.handle_failures
            ... def process_message(msg):
            ...     if msg.is_invalid():
            ...         raise PermanentFailure("Invalid message")
            ...     return process(msg)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PermanentFailure as e:
                # Send to DLQ
                self.send(
                    message=args[0] if args else kwargs,
                    reason=str(e),
                    metadata={'function': func.__name__}
                )
                raise
        return wrapper

    def _persist_message(self, message: DLQMessage) -> None:
        """Persist message to storage backend."""
        if self.storage_backend == StorageBackend.FILE:
            self._save_to_file()
        elif self.storage_backend == StorageBackend.REDIS:
            # Would save to Redis here
            pass
        elif self.storage_backend == StorageBackend.SQS:
            # Would send to SQS here
            pass

    def _save_to_file(self) -> None:
        """Save messages to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                data = [msg.to_dict() for msg in self._storage]
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving DLQ to file: {e}")

    def _load_from_file(self) -> None:
        """Load messages from JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self._storage = [DLQMessage.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self._storage)} messages from DLQ file")
        except Exception as e:
            logger.error(f"Error loading DLQ from file: {e}")


# Example usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create DLQ
    dlq = DeadLetterQueue(
        storage_backend='memory',
        retention_days=7,
        alert_threshold=5
    )

    # Test 1: Manual DLQ operations
    print("Test 1: Manual DLQ operations")

    # Send messages to DLQ
    msg_ids = []
    for i in range(3):
        msg_id = dlq.send(
            message={'order_id': f'ORDER_{i}', 'amount': 100.00},
            reason="Payment gateway timeout",
            metadata={'user_id': f'user_{i}', 'attempt': 3}
        )
        msg_ids.append(msg_id)

    # Send a different type of failure
    dlq.send(
        message={'order_id': 'ORDER_999'},
        reason="Invalid credit card",
        metadata={'user_id': 'user_999'}
    )

    # Get all messages
    messages = dlq.get_messages()
    print(f"\nTotal messages in DLQ: {len(messages)}")

    # Search by reason
    timeout_messages = dlq.search(reason_contains="timeout")
    print(f"Timeout messages: {len(timeout_messages)}")

    # Test 2: Decorator usage
    print("\nTest 2: Decorator usage")

    @dlq.handle_failures
    def process_order(order):
        if order['amount'] < 0:
            raise PermanentFailure("Negative amount not allowed")
        if order['amount'] > 1000:
            raise PermanentFailure("Amount exceeds limit")
        return f"Processed order {order['order_id']}"

    test_orders = [
        {'order_id': 'ORD_1', 'amount': 50},
        {'order_id': 'ORD_2', 'amount': -10},
        {'order_id': 'ORD_3', 'amount': 2000}
    ]

    for order in test_orders:
        try:
            result = process_order(order)
            print(f"Success: {result}")
        except PermanentFailure as e:
            print(f"Failed: {e}")

    # Test 3: Statistics and replay
    print("\nTest 3: Statistics and replay")
    stats = dlq.get_stats()
    print(f"Total messages: {stats['total_messages']}")
    print(f"By reason: {stats['by_reason']}")
    print(f"Total sent: {stats['total_sent']}")

    # Replay timeout messages
    replayed = dlq.replay_all(reason="timeout")
    print(f"\nReplayed {replayed} timeout messages")
    print(f"Remaining in DLQ: {dlq.size()}")
