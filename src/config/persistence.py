"""Settings persistence layer with protocol-based design."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Protocol


class SettingsPersistenceProtocol(Protocol):
    """Protocol defining settings persistence interface."""

    def load(self) -> Dict[str, Any]:
        """
        Load settings from persistent storage.

        Returns:
            Dictionary of settings, empty dict if no settings exist.
        """
        ...

    def save(self, settings: Dict[str, Any]) -> None:
        """
        Save settings to persistent storage.

        Args:
            settings: Dictionary of settings to persist.

        Raises:
            IOError: If unable to save settings.
        """
        ...

    def clear(self) -> None:
        """
        Clear all persisted settings.

        Raises:
            IOError: If unable to clear settings.
        """
        ...


class JSONSettingsPersistence:
    """
    JSON file-based settings persistence.

    Stores settings in a JSON file in the user's home directory.
    """

    def __init__(self, file_path: Optional[Path] = None) -> None:
        """
        Initialize JSON settings persistence.

        Args:
            file_path: Path to settings file. If None, uses default location
                      (~/.voice-to-text/settings.json)
        """
        if file_path is None:
            config_dir = Path.home() / ".voice-to-text"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.file_path = config_dir / "settings.json"
        else:
            self.file_path = file_path
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """
        Load settings from JSON file.

        Returns:
            Dictionary of settings, empty dict if file doesn't exist.
        """
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load settings from {self.file_path}: {e}")
            return {}

    def save(self, settings: Dict[str, Any]) -> None:
        """
        Save settings to JSON file.

        Args:
            settings: Dictionary of settings to persist.

        Raises:
            IOError: If unable to save settings.
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save settings to {self.file_path}: {e}") from e

    def clear(self) -> None:
        """
        Clear all persisted settings by removing the file.

        Raises:
            IOError: If unable to clear settings.
        """
        try:
            if self.file_path.exists():
                self.file_path.unlink()
        except IOError as e:
            raise IOError(f"Failed to clear settings at {self.file_path}: {e}") from e
