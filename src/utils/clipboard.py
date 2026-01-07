"""Clipboard operations for copying text."""

import pyperclip


class ClipboardManager:
    """Manages clipboard operations."""

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        Copy text to system clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False

    @staticmethod
    def get_from_clipboard() -> str:
        """
        Get text from system clipboard.

        Returns:
            Clipboard text, or empty string if failed
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Failed to get from clipboard: {e}")
            return ""
