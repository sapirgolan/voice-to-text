"""Main entry point for the voice-to-text application."""

import sys
from pathlib import Path

from src.audio import AudioFeedback, AudioRecorder
from src.config import Config, JSONSettingsPersistence, SettingsManager
from src.transcription import TranscriptionService
from src.ui import MainWindow


def main() -> int:
    """
    Main application entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Load configuration
        print("Loading configuration...")
        config = Config.load_from_env()
        # Don't require API key from .env - it can be set through UI
        config.validate(require_api_key=False)
        print("Configuration loaded successfully")

        # Initialize settings persistence and manager
        print("Initializing settings manager...")
        persistence = JSONSettingsPersistence()
        settings_manager = SettingsManager(
            persistence=persistence,
            default_api_key=config.api_key,
        )

        # Get effective API key (user override or default)
        effective_api_key = settings_manager.get_api_key()

        # Initialize components
        print("Initializing components...")

        # Audio recorder
        recorder = AudioRecorder(
            sample_rate=config.sample_rate,
            channels=config.channels,
            max_duration=config.max_recording_duration,
        )

        # Transcription service (may start without API key)
        transcription_service = TranscriptionService(
            api_key=effective_api_key,
            client_max_age=config.client_max_age,
            keepalive_expiry=config.keepalive_expiry,
            api_timeout=config.api_timeout,
        )

        # Validate API key if available (skip if network issues during startup)
        if effective_api_key:
            print("Validating OpenAI API key...")
            try:
                if not transcription_service.validate_api_key():
                    print("Warning: Could not validate OpenAI API key")
                    print("The key will be validated when you make your first transcription")
            except Exception as e:
                print(f"Warning: Could not validate API key during startup: {e}")
                print("The key will be validated when you make your first transcription")
        else:
            print("No API key configured. Please enter your OpenAI API key in the application.")

        # Audio feedback
        audio_feedback = AudioFeedback()

        print("Components initialized successfully")

        # Create and run application
        print("Starting application...")
        app = MainWindow(
            recorder=recorder,
            transcription_service=transcription_service,
            audio_feedback=audio_feedback,
            settings_manager=settings_manager,
        )

        app.mainloop()

        return 0

    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
