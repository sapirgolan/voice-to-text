"""Application configuration and settings."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    api_key: Optional[str] = None
    max_recording_duration: int = 300  # 5 minutes in seconds
    sample_rate: int = 16000  # 16kHz optimal for speech recognition
    channels: int = 1  # Mono audio
    audio_format: str = "WAV"
    default_language: str = "en"
    max_retry_attempts: int = 4
    retry_base_delay: float = 1.0  # Seconds for exponential backoff

    # OpenAI client connection settings
    client_max_age: int = 3600  # 1 hour - refresh client after this duration
    keepalive_expiry: float = 300.0  # 5 minutes - keep connections alive
    api_timeout: float = 60.0  # 60 seconds - total timeout for API calls

    @classmethod
    def load_from_env(cls, env_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from .env file.

        Args:
            env_path: Optional path to .env file. If None, searches in current and parent dirs.

        Returns:
            Config instance with loaded settings. API key may be None if not found in .env.
        """
        if env_path:
            load_dotenv(env_path, override=True)
        else:
            # Try to find .env in current or parent directory
            current_dir = Path.cwd()
            for directory in [current_dir, current_dir.parent]:
                env_file = directory / ".env"
                if env_file.exists():
                    load_dotenv(env_file, override=True)
                    break

        api_key = os.getenv("OPENAI_API_KEY")
        return cls(api_key=api_key)

    def validate(self, require_api_key: bool = True) -> None:
        """
        Validate configuration values.

        Args:
            require_api_key: If True, raises error if API key is missing or invalid.
                           If False, skips API key validation.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        if require_api_key:
            if not self.api_key or not self.api_key.startswith("sk-"):
                raise ValueError("Invalid OpenAI API key format. Key should start with 'sk-'")

        if self.max_recording_duration <= 0:
            raise ValueError("Max recording duration must be positive")

        if self.sample_rate not in [8000, 16000, 44100, 48000]:
            raise ValueError(f"Invalid sample rate: {self.sample_rate}")

        if self.channels not in [1, 2]:
            raise ValueError(f"Invalid number of channels: {self.channels}")

        if self.max_retry_attempts < 1:
            raise ValueError("Max retry attempts must be at least 1")

    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """
        Validate API key format (basic check).

        Args:
            api_key: API key to validate.

        Returns:
            True if format is valid, False otherwise.
        """
        return bool(api_key and api_key.startswith("sk-"))
