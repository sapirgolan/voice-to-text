"""Retry strategies for handling transient failures."""

import time
from abc import ABC, abstractmethod
from typing import Protocol


class RetryStrategy(Protocol):
    """Protocol defining retry strategy interface."""

    def should_retry(self, attempt: int) -> bool:
        """
        Determine if another retry attempt should be made.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry attempt.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        ...


class ExponentialBackoffRetry:
    """
    Exponential backoff retry strategy.

    Implements exponential backoff with configurable base delay and maximum attempts.
    """

    def __init__(self, max_attempts: int = 4, base_delay: float = 1.0) -> None:
        """
        Initialize exponential backoff retry strategy.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds (delay = base_delay * 2^attempt)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    def should_retry(self, attempt: int) -> bool:
        """
        Check if another retry should be attempted.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            True if attempt < max_attempts, False otherwise
        """
        return attempt < self.max_attempts

    def get_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds using formula: base_delay * 2^attempt
        """
        return self.base_delay * (2**attempt)

    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function execution

        Raises:
            Exception: The last exception if all retries fail
        """
        attempt = 0
        last_exception = None

        while self.should_retry(attempt):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempt + 1} failed: {e}")

                if self.should_retry(attempt + 1):
                    delay = self.get_delay(attempt)
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

                attempt += 1

        # All retries exhausted
        raise last_exception or Exception("All retry attempts failed")
