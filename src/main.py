"""Main entry point for the voice-to-text application."""

import sys
from pathlib import Path

from src.audio import AudioFeedback, AudioRecorder
from src.config import Config
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
        config.validate()
        print("Configuration loaded successfully")

        # Initialize components
        print("Initializing components...")

        # Audio recorder
        recorder = AudioRecorder(
            sample_rate=config.sample_rate,
            channels=config.channels,
            max_duration=config.max_recording_duration,
        )

        # Transcription service
        transcription_service = TranscriptionService(api_key=config.api_key)

        # Validate API key (skip if network issues during startup)
        print("Validating OpenAI API key...")
        try:
            if not transcription_service.validate_api_key():
                print("Warning: Could not validate OpenAI API key")
                print("The key will be validated when you make your first transcription")
        except Exception as e:
            print(f"Warning: Could not validate API key during startup: {e}")
            print("The key will be validated when you make your first transcription")

        # Audio feedback
        audio_feedback = AudioFeedback()

        print("Components initialized successfully")

        # Create and run application
        print("Starting application...")
        app = MainWindow(
            recorder=recorder,
            transcription_service=transcription_service,
            audio_feedback=audio_feedback,
        )

        app.mainloop()

        return 0

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file in the project root with:")
        print("OPENAI_API_KEY=your-api-key-here")
        return 1

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
