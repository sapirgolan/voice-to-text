"""Transcription service using OpenAI Whisper API."""

import os
from pathlib import Path
from typing import Optional, Protocol

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
    ) -> None:
        """
        Initialize transcription service.

        Args:
            api_key: OpenAI API key (optional - can be set later via update_api_key)
            retry_strategy: Retry strategy for handling failures (default: 4 attempts)
        """
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.retry_strategy = retry_strategy or ExponentialBackoffRetry(
            max_attempts=4, base_delay=1.0
        )

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
            # Network error - should retry
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
        self.client = OpenAI(api_key=api_key)

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
