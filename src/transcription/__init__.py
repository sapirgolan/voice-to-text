"""Transcription module for converting audio to text."""

from .retry_strategy import ExponentialBackoffRetry, RetryStrategy
from .service import TranscriptionService, TranscriptionServiceProtocol

__all__ = [
    "TranscriptionService",
    "TranscriptionServiceProtocol",
    "RetryStrategy",
    "ExponentialBackoffRetry",
]
