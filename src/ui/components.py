"""Reusable UI components for the application."""

from typing import Callable, Optional

import customtkinter as ctk


class LanguageSelector(ctk.CTkComboBox):
    """Language selection dropdown component."""

    LANGUAGES = {
        "English": "en",
        "Hebrew": "he",
    }

    def __init__(self, parent: ctk.CTk, default: str = "English", **kwargs) -> None:
        """
        Initialize language selector.

        Args:
            parent: Parent widget
            default: Default language name (default: "English")
            **kwargs: Additional arguments for CTkComboBox
        """
        super().__init__(
            parent,
            values=list(self.LANGUAGES.keys()),
            **kwargs,
        )
        self.set(default)

    def get_language_code(self) -> str:
        """
        Get the selected language code.

        Returns:
            Language code (e.g., 'en', 'he')
        """
        language_name = self.get()
        return self.LANGUAGES.get(language_name, "en")


class RecordingIndicator(ctk.CTkFrame):
    """
    Visual recording indicator with timer.

    Shows recording status and elapsed time.
    """

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """
        Initialize recording indicator.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="⚫ Ready",
            font=("Arial", 14),
            text_color="gray",
        )
        self.status_label.pack(side="left", padx=10)

        # Timer label
        self.timer_label = ctk.CTkLabel(
            self,
            text="00:00",
            font=("Arial", 14, "bold"),
        )
        self.timer_label.pack(side="left", padx=10)

        self._recording = False
        self._elapsed_seconds = 0

    def start_recording(self) -> None:
        """Update indicator to show recording state."""
        self._recording = True
        self._elapsed_seconds = 0
        self.status_label.configure(text="🔴 Recording", text_color="red")
        self._update_timer()

    def stop_recording(self) -> None:
        """Update indicator to show stopped state."""
        self._recording = False
        self.status_label.configure(text="⚫ Ready", text_color="gray")

    def show_transcribing(self) -> None:
        """Update indicator to show transcription in progress."""
        self.status_label.configure(text="✍️ Transcribing...", text_color="blue")

    def _update_timer(self) -> None:
        """Update the timer display."""
        if not self._recording:
            return

        self._elapsed_seconds += 1
        minutes = self._elapsed_seconds // 60
        seconds = self._elapsed_seconds % 60
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        # Schedule next update
        self.after(1000, self._update_timer)

    def reset(self) -> None:
        """Reset indicator to initial state."""
        self._recording = False
        self._elapsed_seconds = 0
        self.status_label.configure(text="⚫ Ready", text_color="gray")
        self.timer_label.configure(text="00:00")


class TranscriptTextBox(ctk.CTkTextbox):
    """
    Text box for displaying and editing transcribed text.

    Provides a read-write text area with automatic scrolling.
    """

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """
        Initialize transcript text box.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkTextbox
        """
        # Set default values
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("font", ("Arial", 12))
        kwargs.setdefault("height", 200)

        super().__init__(parent, **kwargs)

    def set_text(self, text: str) -> None:
        """
        Set the text content.

        Args:
            text: Text to display
        """
        self.delete("1.0", "end")
        self.insert("1.0", text)

    def get_text(self) -> str:
        """
        Get the current text content.

        Returns:
            Current text in the textbox
        """
        return self.get("1.0", "end-1c")

    def clear(self) -> None:
        """Clear all text."""
        self.delete("1.0", "end")

    def append_text(self, text: str) -> None:
        """
        Append text to the end.

        Args:
            text: Text to append
        """
        self.insert("end", text)
        self.see("end")  # Scroll to end


class StatusBar(ctk.CTkFrame):
    """Status bar for displaying application messages."""

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """
        Initialize status bar.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, height=30, **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Arial", 10),
            anchor="w",
        )
        self.label.pack(fill="x", padx=10, pady=5)

    def set_message(self, message: str, message_type: str = "info") -> None:
        """
        Set status message.

        Args:
            message: Message to display
            message_type: Type of message ('info', 'error', 'success')
        """
        color_map = {
            "info": "gray",
            "error": "red",
            "success": "green",
        }
        color = color_map.get(message_type, "gray")

        self.label.configure(text=message, text_color=color)

        # Auto-clear non-error messages after 5 seconds
        if message_type != "error":
            self.after(5000, lambda: self.label.configure(text="Ready", text_color="gray"))
