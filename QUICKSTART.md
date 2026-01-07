# Quick Start Guide

## Before You Start

**⚠️ macOS Tcl/Tk Issue:** If you see a "macOS version required" error, you need to install Python with updated Tcl/Tk. Quick fix:

```bash
# Install Python 3.11 with proper Tcl/Tk
brew install python@3.11 python-tk@3.11

# Create venv with the new Python
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For more solutions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Getting Started (5 minutes)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Setup API Key
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your key from: https://platform.openai.com/api-keys
```

Your `.env` file should look like:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run the Application
```bash
uv run run.py
```

That's it! 🎉

## Usage

1. **Select Language**: Choose English or Hebrew from the dropdown
2. **Start Recording**: Click "Start Recording" (you'll hear a beep)
3. **Speak**: Speak clearly into your microphone
4. **Stop Recording**: Click "Stop Recording" (you'll hear a beep)
5. **Wait**: The app will transcribe your audio (progress shown)
6. **Review**: Text appears in the text area (already copied to clipboard!)

## Common Issues

### "OPENAI_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that the API key starts with `sk-`
- Don't add quotes around the key in `.env`

### "Microphone permission denied"
- Go to System Preferences → Security & Privacy → Privacy → Microphone
- Enable access for Terminal or Python

### "Failed to start recording"
- Check that a microphone is connected
- Close other apps using the microphone
- Test microphone in System Preferences → Sound → Input

## Available Commands

```bash
# Run the application
uv run run.py

# Or use the installed entry point
uv run voice-to-text

# Run tests (when available)
uv run pytest

# Format code
uv run black src/ tests/

# Type checking
uv run mypy src/
```

## Cost Information

OpenAI Whisper API: **$0.006 per minute** of audio

Examples:
- 1 minute: $0.006
- 5 minutes: $0.03
- 100 minutes/month: $0.60

## Need Help?

- Check README.md for detailed documentation
- Check CLAUDE.md for development guide
- Open an issue on GitHub
