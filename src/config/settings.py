"""Application configuration and settings."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    api_key: str
    max_recording_duration: int = 300  # 5 minutes in seconds
    sample_rate: int = 16000  # 16kHz optimal for speech recognition
    channels: int = 1  # Mono audio
    audio_format: str = "WAV"
    default_language: str = "en"
    max_retry_attempts: int = 4
    retry_base_delay: float = 1.0  # Seconds for exponential backoff

    @classmethod
    def load_from_env(cls, env_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from .env file.

        Args:
            env_path: Optional path to .env file. If None, searches in current and parent dirs.

        Returns:
            Config instance with loaded settings.

        Raises:
            ValueError: If OPENAI_API_KEY is not found in environment.
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
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please create a .env file with your OpenAI API key."
            )

        return cls(api_key=api_key)

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If any configuration value is invalid.
        """
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
