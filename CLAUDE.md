# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voice-to-text desktop application for macOS that converts speech to text using OpenAI's Whisper API. Supports English and Hebrew languages with automatic clipboard integration. Built with clean architecture principles using protocol-based design for testability and maintainability.

**Tech Stack:**
- UI: CustomTkinter (modern tkinter wrapper)
- Audio: sounddevice + soundfile
- Transcription: OpenAI Whisper API
- Configuration: python-dotenv (.env files)

## Development Commands

### Environment Setup

**Using uv (recommended):**
```bash
# Install uv if you haven't already
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv automatically)
uv sync

# Install dev dependencies
uv sync --extra dev

# Install build dependencies
uv sync --extra build
```

**Using traditional pip:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Install build dependencies (for creating .app bundle)
pip install -e ".[build]"
```

### Running the Application
```bash
# Make sure .env file exists with OPENAI_API_KEY
cp .env.example .env
# Edit .env and add your API key

# Run with uv (recommended)
uv run run.py

# Or run with installed script
uv run voice-to-text

# Or activate venv and run directly
source .venv/bin/activate
python src/main.py
```

### Testing
```bash
# With uv
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_recorder.py

# Or with activated venv
source .venv/bin/activate
pytest
```

### Code Quality
```bash
# Format code with black
uv run black src/ tests/

# Type checking with mypy
uv run mypy src/

# Or with activated venv
source .venv/bin/activate
black src/ tests/
mypy src/
```

### Building .app Bundle
```bash
# Create macOS .app bundle
python setup.py py2app

# Output will be in dist/Voice to Text.app
```

## Project Architecture

The project follows clean architecture with clear separation of concerns:

```
src/
├── audio/              # Audio layer (recording, feedback)
│   ├── recorder.py     # AudioRecorder with protocol-based design
│   └── audio_feedback.py  # Beep sounds for user feedback
├── transcription/      # Transcription layer
│   ├── service.py      # OpenAI Whisper API client
│   └── retry_strategy.py  # Exponential backoff retry logic
├── ui/                 # Presentation layer
│   ├── main_window.py  # Main application window
│   └── components.py   # Reusable UI components
├── config/             # Configuration layer
│   └── settings.py     # Settings loaded from .env
├── utils/              # Cross-cutting utilities
│   ├── clipboard.py    # Clipboard operations
│   └── threading_utils.py  # Threading helpers
└── main.py             # Application entry point
```

### Key Design Patterns

**Protocol-Based Design:**
- `AudioRecorderProtocol` - defines interface for audio recording
- `TranscriptionServiceProtocol` - defines interface for transcription
- Enables easy mocking for tests and future implementations

**Dependency Injection:**
- Components receive dependencies via constructor
- UI layer depends on abstractions, not concrete implementations
- Example: `MainWindow(recorder, transcription_service, audio_feedback)`

**Threading for Non-Blocking Operations:**
- Audio recording runs in separate thread
- Transcription API calls run in background threads
- UI remains responsive during long operations
- Use `run_in_thread_with_callback` for async operations with callbacks

### Key Implementation Details

**Audio Recording:**
- Uses sounddevice with callback-based streaming
- Records at 16kHz mono (optimal for speech recognition)
- Max duration: 5 minutes (300 seconds)
- Saves to temporary WAV file (PCM 16-bit)

**Transcription:**
- OpenAI Whisper API via official Python client
- Automatic retry with exponential backoff (4 attempts)
- Supports language codes: 'en' (English), 'he' (Hebrew)
- Max file size: 25 MB (enforced by API)

**Error Handling:**
- Retry transient failures (network, rate limit, server errors)
- Don't retry client errors (400, 401, etc.)
- Display user-friendly error messages in status bar
- Play error beep for failed transcriptions

## Configuration

Configuration is managed via `.env` file:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

Hardcoded settings in `src/config/settings.py`:
- `max_recording_duration`: 300 seconds (5 minutes)
- `sample_rate`: 16000 Hz
- `channels`: 1 (mono)
- `max_retry_attempts`: 4
- `retry_base_delay`: 1.0 seconds

## Adding New Features

**Adding a New Language:**
1. Add language to `LanguageSelector.LANGUAGES` dict in `src/ui/components.py`
2. Use ISO 639-1 code (e.g., 'es' for Spanish)
3. No other changes needed - Whisper API supports 99+ languages

**Adding New Transcription Provider:**
1. Create new service implementing `TranscriptionServiceProtocol`
2. Update `src/main.py` to instantiate new service
3. Pass to `MainWindow` constructor

**Customizing UI:**
- UI components are in `src/ui/components.py`
- Main window layout in `src/ui/main_window.py`
- CustomTkinter uses tkinter-like API with modern appearance

## Common Pitfalls

1. **Threading Issues:** Always use `run_in_thread_with_callback` for long-running operations, never block the UI thread
2. **Audio Permissions:** macOS requires microphone permission - app will prompt on first use
3. **API Key Validation:** Always validate API key before attempting transcription
4. **File Cleanup:** Temporary audio files are created in system temp dir - consider cleanup on exit
5. **Max Recording Duration:** Recording automatically stops at 5 minutes to prevent file size issues

## Testing Notes

- Mock `AudioRecorderProtocol` for UI tests
- Mock `TranscriptionServiceProtocol` for integration tests
- Use `pytest-cov` for coverage reports
- Test retry logic with network failures