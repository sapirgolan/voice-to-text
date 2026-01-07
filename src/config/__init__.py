"""Configuration module for voice-to-text application."""

from .persistence import JSONSettingsPersistence, SettingsPersistenceProtocol
from .settings import Config
from .settings_manager import SettingsManager, SettingsManagerProtocol

__all__ = [
    "Config",
    "SettingsManager",
    "SettingsManagerProtocol",
    "SettingsPersistenceProtocol",
    "JSONSettingsPersistence",
]
