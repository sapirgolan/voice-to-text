# Fixing Safe-chain Network Blocking

## Problem

If you see these errors when running the app:
```
Safe-chain: connect to api.openai.com:443 timed out after 30000ms
Safe-chain: Closing connection because previously timedout connect to api.openai.com
```

This means `uv`'s Safe-chain security feature is blocking network connections to OpenAI's API.

## Solutions

### Solution 1: Run with Safe-chain Disabled (Recommended for Development)

Run the application with Safe-chain disabled:

```bash
# Disable Safe-chain for this run
uv run --no-safe-chain run.py

# Or set environment variable
UV_NO_SAFE_CHAIN=1 uv run run.py
```

### Solution 2: Allow OpenAI API in Safe-chain Config

Create a Safe-chain allowlist configuration:

```bash
# Create uv config directory if it doesn't exist
mkdir -p ~/.config/uv

# Create or edit the config file
cat > ~/.config/uv/uv.toml << 'EOF'
[safe-chain]
# Allow OpenAI API connections
allow-hosts = [
    "api.openai.com",
    "*.openai.com"
]
EOF
```

Then run normally:
```bash
uv run run.py
```

### Solution 3: Use Python Directly (Bypass uv)

If you don't need uv's features, run with Python directly:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run with Python
python src/main.py

# Or run the wrapper script
python run.py
```

### Solution 4: Run Without uv Entirely

```bash
# Install dependencies with pip instead of uv
source .venv/bin/activate
pip install -e .

# Run the application
python src/main.py
```

## Testing the Fix

After applying any solution, test the connection:

```bash
# Test API connection directly
python -c "
from src.config import Config
from src.transcription import TranscriptionService

config = Config.load_from_env()
service = TranscriptionService(api_key=config.api_key)
print('Testing API connection...')
result = service.validate_api_key()
print(f'Connection successful: {result}')
"
```

Expected output:
```
Testing API connection...
Connection successful: True
```

## Why This Happens

`uv` includes a security feature called "Safe-chain" that monitors and controls network connections from Python packages. This is designed to prevent supply chain attacks where malicious packages make unauthorized network connections.

For development purposes with trusted packages like `openai`, you can safely disable this feature or add api.openai.com to the allowlist.

## Recommended Approach

For **development**: Use Solution 1 (`--no-safe-chain` flag)
For **production**: Use Solution 2 (configure allowlist)

## Quick Start Command

The simplest way to run the app:

```bash
uv run --no-safe-chain run.py
```

Or add this alias to your shell profile:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias run-voice="cd /path/to/voice-to-text && uv run --no-safe-chain run.py"
```
