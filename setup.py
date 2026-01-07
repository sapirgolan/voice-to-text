"""
py2app setup script for building macOS .app bundle.

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["src/main.py"]
DATA_FILES = [
    (".", [".env.example"]),
]
OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "customtkinter",
        "sounddevice",
        "soundfile",
        "numpy",
        "openai",
        "dotenv",
        "pyperclip",
    ],
    "includes": [
        "PIL",
        "cffi",
    ],
    "excludes": [
        "matplotlib",
        "scipy",
        "pandas",
    ],
    "plist": {
        "CFBundleName": "Voice to Text",
        "CFBundleDisplayName": "Voice to Text",
        "CFBundleIdentifier": "com.voicetotext.app",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "NSMicrophoneUsageDescription": "This app needs access to the microphone to record audio for transcription.",
        "LSMinimumSystemVersion": "10.13.0",
    },
    "iconfile": None,  # Add path to .icns file if you have one
}

setup(
    name="Voice to Text",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
