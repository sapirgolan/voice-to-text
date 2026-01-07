"""Settings manager for runtime configuration management."""

from typing import Callable, Optional, Protocol

from .persistence import SettingsPersistenceProtocol


class SettingsManagerProtocol(Protocol):
    """Protocol defining settings manager interface."""

    def get_api_key(self) -> Optional[str]:
        """
        Get the current API key (runtime override or default).

        Returns:
            API key string or None if not set.
        """
        ...

    def update_api_key(self, api_key: str, validator: Callable[[str], bool]) -> bool:
        """
        Update the API key after validation.

        Args:
            api_key: New API key to set.
            validator: Function to validate the API key.

        Returns:
            True if key was validated and saved, False otherwise.
        """
        ...

    def reset_api_key(self) -> Optional[str]:
        """
        Reset to the default API key from .env file.

        Returns:
            The default API key, or None if not available.
        """
        ...

    def has_runtime_override(self) -> bool:
        """
        Check if there's a runtime API key override.

        Returns:
            True if user has set a custom API key, False otherwise.
        """
        ...


class SettingsManager:
    """
    Manages application settings with runtime overrides.

    Provides a clean interface for managing user settings that override
    default configuration values from .env files.
    """

    def __init__(
        self,
        persistence: SettingsPersistenceProtocol,
        default_api_key: Optional[str] = None,
    ) -> None:
        """
        Initialize settings manager.

        Args:
            persistence: Persistence layer for saving/loading settings.
            default_api_key: Default API key from .env file (optional).
        """
        self.persistence = persistence
        self.default_api_key = default_api_key
        self._runtime_api_key: Optional[str] = None

        # Load persisted settings
        self._load_persisted_settings()

    def _load_persisted_settings(self) -> None:
        """Load persisted settings from storage."""
        settings = self.persistence.load()
        self._runtime_api_key = settings.get("api_key")

    def get_api_key(self) -> Optional[str]:
        """
        Get the current API key (runtime override or default).

        Returns:
            API key string or None if not set.
        """
        return self._runtime_api_key or self.default_api_key

    def update_api_key(self, api_key: str, validator: Callable[[str], bool]) -> bool:
        """
        Update the API key after validation.

        Args:
            api_key: New API key to set.
            validator: Function to validate the API key (should return True if valid).

        Returns:
            True if key was validated and saved, False otherwise.
        """
        # Validate the key
        if not validator(api_key):
            return False

        # Save to persistence
        try:
            settings = self.persistence.load()
            settings["api_key"] = api_key
            self.persistence.save(settings)

            # Update runtime state
            self._runtime_api_key = api_key
            return True

        except IOError as e:
            print(f"Failed to save API key: {e}")
            return False

    def reset_api_key(self) -> Optional[str]:
        """
        Reset to the default API key from .env file.

        Clears any runtime override and returns to using the default key.

        Returns:
            The default API key, or None if not available.
        """
        try:
            # Clear from persistence
            settings = self.persistence.load()
            if "api_key" in settings:
                del settings["api_key"]
                self.persistence.save(settings)

            # Clear runtime override
            self._runtime_api_key = None
            return self.default_api_key

        except IOError as e:
            print(f"Failed to reset API key: {e}")
            return None

    def has_runtime_override(self) -> bool:
        """
        Check if there's a runtime API key override.

        Returns:
            True if user has set a custom API key, False otherwise.
        """
        return self._runtime_api_key is not None
