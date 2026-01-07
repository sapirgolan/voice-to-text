# Troubleshooting Guide

## macOS Tcl/Tk Version Issues

### Error: "macOS 15 (1507) or later required"

**Cause:** The system Python on macOS comes with an outdated Tcl/Tk version (8.5), but CustomTkinter requires Tcl/Tk 8.6+.

**Solution 1: Install Python with updated Tcl/Tk via Homebrew (Recommended)**

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11 or 3.12 with Tcl/Tk support
brew install python@3.11 python-tk@3.11

# Create a new virtual environment with Homebrew Python
python3.11 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the application
python src/main.py
```

**Solution 2: Use pyenv to install a Python with proper Tcl/Tk**

```bash
# Install pyenv
brew install pyenv

# Install Python 3.11 with Tcl/Tk support
pyenv install 3.11.7

# Set it as the local version for this project
pyenv local 3.11.7

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the application
python src/main.py
```

**Solution 3: Install python3-tk for your Python version**

```bash
# For Python 3.9
brew install python-tk@3.9

# Reinstall with the updated Python
rm -rf .venv
python3.9 -m venv .venv
source .venv/bin/activate
pip install -e .
python src/main.py
```

### Verify Your Tk Installation

After installing, verify you have a compatible Tk version:

```bash
python -c "import tkinter; print(f'Tk version: {tkinter.TkVersion}')"
```

You should see `8.6` or higher.

## API Key Issues

### Error: "Invalid OpenAI API key"

**Cause:** The API key in `.env` is invalid, expired, or incorrectly formatted.

**Solution:**

1. Get a new API key from https://platform.openai.com/api-keys
2. Update `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Make sure there are no quotes around the key
4. Make sure there are no spaces before or after the key

## Microphone Permission Issues

### Error: "Failed to start recording" or "No input devices found"

**Cause:** macOS hasn't granted microphone permission, or no microphone is connected.

**Solution:**

1. Go to **System Preferences → Security & Privacy → Privacy → Microphone**
2. Enable access for **Terminal** or **Python**
3. If using Terminal, you may need to restart it
4. Verify your microphone is connected and working:
   - Go to **System Preferences → Sound → Input**
   - Speak and check if the input level meter moves

## Audio Recording Issues

### Recording is silent or low quality

**Solutions:**

1. **Check input device:**
   - Go to **System Preferences → Sound → Input**
   - Select the correct microphone
   - Adjust input volume

2. **Test microphone separately:**
   ```bash
   # Record a 5-second test
   rec -r 16000 -c 1 test.wav trim 0 5

   # Play it back
   play test.wav
   ```

3. **Close other applications** using the microphone (Zoom, Discord, etc.)

## Transcription Issues

### Transcription is slow

**Normal behavior:** API calls typically take 2-10 seconds depending on audio length and network speed.

### Transcription fails after retries

**Possible causes:**
1. **No internet connection** - Whisper API requires internet
2. **Rate limiting** - Too many requests in a short time
3. **Server issues** - OpenAI service temporarily unavailable

**Solutions:**
1. Check your internet connection
2. Wait a minute and try again
3. Check OpenAI status page: https://status.openai.com/

### Transcription is inaccurate

**Solutions:**
1. **Speak clearly** and at a moderate pace
2. **Reduce background noise**
3. **Use a better microphone** (USB microphones are better than built-in)
4. **Check language selection** - Make sure you selected the correct language

## Installation Issues

### Error: "No module named 'customtkinter'" or similar

**Solution:**

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -e .

# Or with uv
uv sync
```

### Error: "Failed to build sounddevice"

**Cause:** Missing system dependencies for audio libraries.

**Solution (macOS):**

```bash
# Install portaudio
brew install portaudio

# Reinstall
pip install --force-reinstall sounddevice
```

## Building .app Bundle Issues

### py2app build fails

**Common causes:**
1. Missing dependencies
2. Incorrect Python version
3. Virtual environment issues

**Solution:**

```bash
# Clean previous builds
rm -rf build/ dist/

# Install build dependencies
pip install -e ".[build]"

# Build
python setup.py py2app
```

### .app bundle won't open

**Cause:** Code signing or permissions issues on macOS.

**Solution:**

```bash
# Remove quarantine attribute
xattr -cr "dist/Voice to Text.app"

# Try running it
open "dist/Voice to Text.app"
```

## Still Having Issues?

1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Create a new issue with:
   - Your macOS version (`sw_vers`)
   - Your Python version (`python --version`)
   - Your Tk version (`python -c "import tkinter; print(tkinter.TkVersion)"`)
   - The full error message
   - Steps to reproduce
