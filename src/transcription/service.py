"""Transcription service using OpenAI Whisper API."""

import os
import time
from pathlib import Path
from typing import Optional, Protocol

import httpx
from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from .retry_strategy import ExponentialBackoffRetry


class TranscriptionServiceProtocol(Protocol):
    """Protocol defining transcription service interface."""

    def transcribe(self, audio_file_path: Path, language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file
            language: Language code (e.g., 'en', 'he') or None for auto-detection

        Returns:
            Transcribed text

        Raises:
            TranscriptionError: If transcription fails after all retries
        """
        ...


class TranscriptionError(Exception):
    """Exception raised when transcription fails."""

    pass


class TranscriptionService:
    """
    OpenAI Whisper API transcription service.

    Provides audio-to-text transcription with automatic retry on transient failures.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        retry_strategy: Optional[ExponentialBackoffRetry] = None,
        client_max_age: int = 3600,
        keepalive_expiry: float = 300.0,
        api_timeout: float = 60.0,
    ) -> None:
        """
        Initialize transcription service.

        Args:
            api_key: OpenAI API key (optional - can be set later via update_api_key)
            retry_strategy: Retry strategy for handling failures (default: 4 attempts)
            client_max_age: Maximum age of client in seconds before refresh (default: 1 hour)
            keepalive_expiry: Connection keep-alive duration in seconds (default: 5 minutes)
            api_timeout: Total timeout for API calls in seconds (default: 60 seconds)
        """
        self.api_key = api_key
        self.retry_strategy = retry_strategy or ExponentialBackoffRetry(
            max_attempts=4, base_delay=1.0
        )
        self.client_max_age = client_max_age
        self.keepalive_expiry = keepalive_expiry
        self.api_timeout = api_timeout
        self._last_use_time: Optional[float] = None
        self.client: Optional[OpenAI] = None
        self._create_client()

    def _create_client(self) -> None:
        """
        Create or recreate the OpenAI client with connection pool configuration.

        Configures httpx with:
        - Extended keep-alive timeout to prevent premature connection closure
        - Proper timeout settings to avoid hanging on stale connections
        """
        # Close existing client's HTTP client to prevent resource leaks
        if self.client is not None:
            try:
                # Access the underlying httpx client and close it
                if hasattr(self.client, '_client') and hasattr(self.client._client, 'close'):
                    self.client._client.close()
            except Exception as e:
                print(f"Warning: Failed to close old httpx client: {e}")

        if not self.api_key:
            self.client = None
            self._last_use_time = None
            return

        # Configure httpx client with NO connection pooling
        # Connection pooling causes stale connection timeouts after idle periods
        # Set max_keepalive_connections=0 to disable pooling and force fresh connections
        http_client = httpx.Client(
            timeout=httpx.Timeout(
                timeout=self.api_timeout,
                connect=self.api_timeout,
                read=self.api_timeout,
                write=30.0,
                pool=10.0,
            ),
            limits=httpx.Limits(
                max_keepalive_connections=0,  # Disable connection pooling
                max_connections=10,  # Limit concurrent connections
            ),
        )

        self.client = OpenAI(api_key=self.api_key, http_client=http_client)
        self._last_use_time = time.time()
        print(f"OpenAI client created/refreshed at {time.strftime('%H:%M:%S')}")

    def _ensure_fresh_client(self) -> None:
        """
        Ensure the client is fresh and ready to use.

        Recreates the client if:
        - No client exists
        - Client is older than client_max_age (prevents long-term staleness)
        """
        if self.client is None:
            print("No client exists, creating new one")
            self._create_client()
            return

        if self._last_use_time is None:
            print("No last use time recorded, creating new client")
            self._create_client()
            return

        age = time.time() - self._last_use_time
        if age > self.client_max_age:
            print(
                f"Client is {age:.0f}s old (max: {self.client_max_age}s), creating new client"
            )
            self._create_client()

    def transcribe(self, audio_file_path: Path, language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper API.

        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'he') or None for auto-detection

        Returns:
            Transcribed text as string

        Raises:
            TranscriptionError: If transcription fails after all retries
            ValueError: If audio file doesn't exist or is too large or API key not set
        """
        # Ensure we have a fresh, working client
        self._ensure_fresh_client()

        # Validate API key is set
        if not self.client:
            raise ValueError("API key not set. Please configure your OpenAI API key.")

        # Validate input
        if not audio_file_path.exists():
            raise ValueError(f"Audio file not found: {audio_file_path}")

        file_size = audio_file_path.stat().st_size
        max_size = 25 * 1024 * 1024  # 25 MB
        if file_size > max_size:
            raise ValueError(
                f"Audio file too large: {file_size / (1024*1024):.2f} MB "
                f"(max: {max_size / (1024*1024):.2f} MB)"
            )

        # Execute transcription with retry
        try:
            result = self.retry_strategy.execute_with_retry(
                self._transcribe_once, audio_file_path, language
            )
            return result
        except Exception as e:
            raise TranscriptionError(
                f"Transcription failed after {self.retry_strategy.max_attempts} attempts: {e}"
            ) from e

    def _transcribe_once(self, audio_file_path: Path, language: Optional[str]) -> str:
        """
        Single transcription attempt without retry logic.

        Args:
            audio_file_path: Path to audio file
            language: Language code or None

        Returns:
            Transcribed text

        Raises:
            Various OpenAI API exceptions
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                params = {
                    "model": "whisper-1",
                    "file": audio_file,
                }

                if language:
                    params["language"] = language

                transcript = self.client.audio.transcriptions.create(**params)
                return transcript.text

        except RateLimitError as e:
            # Rate limit - should retry
            raise TranscriptionError(f"Rate limit exceeded: {e}") from e

        except APIConnectionError as e:
            # Network error - could be stale connection, recreate client for next retry
            print("Connection error detected, will recreate client for next attempt")
            self._create_client()
            raise TranscriptionError(f"Connection error: {e}") from e

        except APIError as e:
            # General API error - may or may not be retryable
            if e.status_code in [500, 502, 503, 504]:
                # Server errors - should retry
                raise TranscriptionError(f"Server error: {e}") from e
            else:
                # Client errors (400, 401, etc.) - should not retry
                raise TranscriptionError(f"API error: {e}") from e

        except Exception as e:
            # Unexpected error
            raise TranscriptionError(f"Unexpected error: {e}") from e

    def update_api_key(self, api_key: str) -> None:
        """
        Update the API key and recreate the OpenAI client.

        Args:
            api_key: New OpenAI API key
        """
        self.api_key = api_key
        self._create_client()

    def validate_api_key(self, api_key: Optional[str] = None) -> bool:
        """
        Validate that an API key is working.

        Args:
            api_key: Optional API key to validate. If None, validates current client.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # If a specific key is provided, create a temporary client
            client = OpenAI(api_key=api_key) if api_key else self.client

            if not client:
                return False

            # Try to list models as a simple validation
            client.models.list()
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False
