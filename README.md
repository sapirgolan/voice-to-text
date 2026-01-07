# Voice to Text Application

A macOS desktop application for converting speech to text using OpenAI's Whisper API. Supports English and Hebrew languages with automatic clipboard integration.

## Features

- 🎤 **Audio Recording**: Record up to 5 minutes of audio from your microphone
- 🌍 **Multi-language Support**: English and Hebrew transcription
- 🔄 **Automatic Retry**: Robust error handling with 4 retry attempts
- 📋 **Clipboard Integration**: Automatically copies transcribed text to clipboard
- ✏️ **Editable Output**: Edit transcribed text before copying
- 🔊 **Audio Feedback**: Beep sounds indicate recording start/stop
- ⏱️ **Real-time Timer**: Visual indicator showing recording duration

## Requirements

- macOS 10.13 or later
- Python 3.9 or later (with Tcl/Tk 8.6+)
- OpenAI API key

**⚠️ Important:** The default Python on macOS comes with an outdated Tcl/Tk version. If you get a "macOS version required" error, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md#macos-tcltk-version-issues) for solutions.

## Installation

### For Development

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-to-text
```

2. Install dependencies with uv (recommended):
```bash
# Install uv if you haven't already
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv automatically)
uv sync
```

Or use traditional pip:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run the application:
```bash
# With uv (recommended)
uv run run.py

# Or activate venv and run directly
source .venv/bin/activate
python src/main.py

# Or use the installed script
uv run voice-to-text
```

### For End Users (Standalone .app)

1. Download the .app bundle from releases
2. Drag to Applications folder
3. Create a `.env` file in the same directory as the app with your OpenAI API key
4. Double-click to run

## Building .app Bundle

To create a standalone macOS application:

```bash
# Install build dependencies
pip install -e ".[build]"

# Build the .app bundle
python setup.py py2app

# The .app will be in dist/Voice to Text.app
```

## Usage

1. **Select Language**: Choose English or Hebrew from the dropdown
2. **Start Recording**: Click "Start Recording" button (you'll hear a beep)
3. **Speak**: Speak clearly into your microphone
4. **Stop Recording**: Click "Stop Recording" when done (you'll hear a beep)
5. **Wait for Transcription**: The app will transcribe your audio (progress shown)
6. **Review and Edit**: The transcribed text appears in the text area (already copied to clipboard)
7. **Manual Copy**: Click "Copy to Clipboard" to copy edited text

## Configuration

Configuration is loaded from `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### Advanced Configuration

You can modify settings in `src/config/settings.py`:

- `max_recording_duration`: Maximum recording length (default: 300 seconds)
- `sample_rate`: Audio sample rate (default: 16000 Hz)
- `max_retry_attempts`: Number of retry attempts for transcription (default: 4)

## Architecture

The application follows clean architecture principles:

```
src/
├── audio/              # Audio recording and feedback
│   ├── recorder.py     # Audio recording with protocol
│   └── audio_feedback.py  # Beep sounds
├── transcription/      # Transcription service
│   ├── service.py      # OpenAI Whisper client
│   └── retry_strategy.py  # Retry logic
├── ui/                 # User interface
│   ├── main_window.py  # Main application window
│   └── components.py   # Reusable UI components
├── config/             # Configuration management
│   └── settings.py     # App settings
├── utils/              # Utility functions
│   ├── clipboard.py    # Clipboard operations
│   └── threading_utils.py  # Threading helpers
└── main.py             # Application entry point
```

## Dependencies

Core dependencies:
- `customtkinter` - Modern UI framework
- `sounddevice` - Audio recording
- `soundfile` - Audio file handling
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `pyperclip` - Clipboard operations

## Troubleshooting

### Microphone Permission Denied
- Go to System Preferences → Security & Privacy → Privacy → Microphone
- Enable access for Python or the Voice to Text app

### API Key Not Found
- Ensure `.env` file exists in the project root
- Check that `OPENAI_API_KEY` is set correctly
- API key should start with `sk-`

### Audio Recording Issues
- Check that a microphone is connected
- Test microphone in System Preferences → Sound → Input
- Close other applications using the microphone

### Transcription Fails
- Check internet connection (API requires internet)
- Verify OpenAI API key is valid
- Check OpenAI account has sufficient credits

## Cost Information

OpenAI Whisper API pricing: $0.006 per minute of audio

Example costs:
- 1 minute recording: $0.006
- 5 minute recording: $0.03
- 100 minutes/month: $0.60

## License

[Your License Here]

## Support

For issues and feature requests, please open an issue on GitHub.
