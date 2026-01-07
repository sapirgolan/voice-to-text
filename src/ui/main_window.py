"""Main application window."""

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from ..audio import AudioFeedback, AudioRecorder
from ..config import SettingsManager
from ..transcription import TranscriptionService
from ..utils import ClipboardManager, run_in_thread_with_callback
from .components import ApiKeyInput, LanguageSelector, RecordingIndicator, StatusBar, TranscriptTextBox


class MainWindow(ctk.CTk):
    """Main application window for voice-to-text."""

    def __init__(
        self,
        recorder: AudioRecorder,
        transcription_service: TranscriptionService,
        audio_feedback: AudioFeedback,
        settings_manager: SettingsManager,
    ) -> None:
        """
        Initialize main window.

        Args:
            recorder: Audio recorder instance
            transcription_service: Transcription service instance
            audio_feedback: Audio feedback instance
            settings_manager: Settings manager instance
        """
        super().__init__()

        self.recorder = recorder
        self.transcription_service = transcription_service
        self.audio_feedback = audio_feedback
        self.settings_manager = settings_manager
        self.clipboard = ClipboardManager()

        self._setup_window()
        self._create_widgets()
        self._layout_widgets()
        self._initialize_api_key_display()

    def _setup_window(self) -> None:
        """Setup window properties."""
        self.title("Voice to Text")
        self.geometry("600x500")
        self.resizable(True, True)

        # Set appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Voice to Text Transcription",
            font=("Arial", 20, "bold"),
        )

        # API Key settings frame
        self.api_key_frame = ctk.CTkFrame(self)
        self.api_key_label = ctk.CTkLabel(
            self.api_key_frame,
            text="API Key:",
            font=("Arial", 12),
        )
        self.api_key_input = ApiKeyInput(self.api_key_frame, width=300)
        self.api_key_apply_button = ctk.CTkButton(
            self.api_key_frame,
            text="Apply",
            command=self._on_apply_api_key,
            width=80,
        )
        self.api_key_reset_button = ctk.CTkButton(
            self.api_key_frame,
            text="Reset to Default",
            command=self._on_reset_api_key,
            width=120,
        )

        # Language selector
        self.language_frame = ctk.CTkFrame(self)
        self.language_label = ctk.CTkLabel(
            self.language_frame,
            text="Language:",
            font=("Arial", 12),
        )
        self.language_selector = LanguageSelector(
            self.language_frame,
            default="English",
            width=150,
        )

        # Recording indicator
        self.recording_indicator = RecordingIndicator(self)

        # Control buttons
        self.button_frame = ctk.CTkFrame(self)
        self.record_button = ctk.CTkButton(
            self.button_frame,
            text="Start Recording",
            command=self._on_record_button_click,
            width=200,
            height=50,
            font=("Arial", 14, "bold"),
            fg_color="green",
            hover_color="darkgreen",
        )

        # Transcript text area
        self.transcript_label = ctk.CTkLabel(
            self,
            text="Transcription:",
            font=("Arial", 12),
            anchor="w",
        )
        self.transcript_textbox = TranscriptTextBox(self)

        # Copy button
        self.copy_button = ctk.CTkButton(
            self,
            text="Copy to Clipboard",
            command=self._on_copy_button_click,
            width=150,
        )

        # Status bar
        self.status_bar = StatusBar(self)

    def _layout_widgets(self) -> None:
        """Layout all widgets."""
        # Title
        self.title_label.pack(pady=20)

        # API Key frame
        self.api_key_frame.pack(pady=10, fill="x", padx=20)
        self.api_key_label.pack(side="left", padx=10)
        self.api_key_input.pack(side="left", padx=5)
        self.api_key_apply_button.pack(side="left", padx=5)
        self.api_key_reset_button.pack(side="left", padx=5)

        # Language selector
        self.language_frame.pack(pady=10, fill="x", padx=20)
        self.language_label.pack(side="left", padx=10)
        self.language_selector.pack(side="left", padx=10)

        # Recording indicator
        self.recording_indicator.pack(pady=10)

        # Control buttons
        self.button_frame.pack(pady=20)
        self.record_button.pack()

        # Transcript
        self.transcript_label.pack(pady=(20, 5), padx=20, anchor="w")
        self.transcript_textbox.pack(pady=5, padx=20, fill="both", expand=True)

        # Copy button
        self.copy_button.pack(pady=10)

        # Status bar
        self.status_bar.pack(side="bottom", fill="x")

    def _on_record_button_click(self) -> None:
        """Handle record button click."""
        if self.recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Start recording audio."""
        try:
            # Clear previous transcript
            self.transcript_textbox.clear()

            # Update UI
            self.record_button.configure(
                text="Stop Recording",
                fg_color="red",
                hover_color="darkred",
            )
            self.language_selector.configure(state="disabled")
            self.recording_indicator.start_recording()
            self.status_bar.set_message("Recording...", "info")

            # Play start beep
            self.audio_feedback.play_start_beep()

            # Start recording
            self.recorder.start_recording()

        except Exception as e:
            self._handle_error(f"Failed to start recording: {e}")
            self._reset_ui()

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        try:
            # Update UI
            self.record_button.configure(state="disabled")
            self.recording_indicator.stop_recording()
            self.status_bar.set_message("Saving recording...", "info")

            # Play stop beep
            self.audio_feedback.play_stop_beep()

            # Stop recording (in thread to avoid blocking)
            run_in_thread_with_callback(
                self.recorder.stop_recording,
                callback=self._on_recording_stopped,
                error_callback=self._on_recording_error,
            )

        except Exception as e:
            self._handle_error(f"Failed to stop recording: {e}")
            self._reset_ui()

    def _on_recording_stopped(self, audio_file_path: Optional[Path]) -> None:
        """
        Callback when recording is stopped (called from background thread).

        Args:
            audio_file_path: Path to recorded audio file
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_recording_stopped(audio_file_path))

    def _handle_recording_stopped(self, audio_file_path: Optional[Path]) -> None:
        """
        Handle recording stopped on main thread (thread-safe).

        Args:
            audio_file_path: Path to recorded audio file
        """
        if not audio_file_path:
            self._handle_error("No audio was recorded")
            self._reset_ui()
            return

        # Update UI
        self.recording_indicator.show_transcribing()
        self.status_bar.set_message("Transcribing audio...", "info")

        # Get selected language
        language = self.language_selector.get_language_code()

        # Start transcription in background
        run_in_thread_with_callback(
            self.transcription_service.transcribe,
            callback=self._on_transcription_complete,
            error_callback=self._on_transcription_error,
            audio_file_path=audio_file_path,
            language=language,
        )

    def _on_recording_error(self, error: Exception) -> None:
        """
        Callback when recording fails (called from background thread).

        Args:
            error: Exception that occurred
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_recording_error(error))

    def _handle_recording_error(self, error: Exception) -> None:
        """
        Handle recording error on main thread (thread-safe).

        Args:
            error: Exception that occurred
        """
        self._handle_error(f"Recording error: {error}")
        self._reset_ui()

    def _on_transcription_complete(self, transcript: str) -> None:
        """
        Callback when transcription is complete (called from background thread).

        Args:
            transcript: Transcribed text
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_transcription_complete(transcript))

    def _handle_transcription_complete(self, transcript: str) -> None:
        """
        Handle transcription completion on main thread (thread-safe).

        Args:
            transcript: Transcribed text
        """
        # Update UI
        self.transcript_textbox.set_text(transcript)
        self.status_bar.set_message("Transcription complete!", "success")

        # Copy to clipboard
        if self.clipboard.copy_to_clipboard(transcript):
            self.status_bar.set_message(
                "Transcription complete and copied to clipboard!", "success"
            )

        self._reset_ui()

    def _on_transcription_error(self, error: Exception) -> None:
        """
        Callback when transcription fails (called from background thread).

        Args:
            error: Exception that occurred
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_transcription_error(error))

    def _handle_transcription_error(self, error: Exception) -> None:
        """
        Handle transcription error on main thread (thread-safe).

        Args:
            error: Exception that occurred
        """
        self.audio_feedback.play_error_beep()
        self._handle_error(f"Transcription failed: {error}")
        self._reset_ui()

    def _on_copy_button_click(self) -> None:
        """Handle copy button click."""
        text = self.transcript_textbox.get_text()
        if not text or text.strip() == "":
            self.status_bar.set_message("No text to copy", "error")
            return

        if self.clipboard.copy_to_clipboard(text):
            self.status_bar.set_message("Copied to clipboard!", "success")
        else:
            self.status_bar.set_message("Failed to copy to clipboard", "error")

    def _handle_error(self, message: str) -> None:
        """
        Handle error by displaying message.

        Args:
            message: Error message to display
        """
        print(f"Error: {message}")
        self.status_bar.set_message(message, "error")

    def _reset_ui(self) -> None:
        """Reset UI to initial state."""
        self.record_button.configure(
            text="Start Recording",
            fg_color="green",
            hover_color="darkgreen",
            state="normal",
        )
        self.language_selector.configure(state="normal")
        self.recording_indicator.reset()

    def _initialize_api_key_display(self) -> None:
        """Initialize API key input field with current value."""
        current_key = self.settings_manager.get_api_key()
        if current_key:
            self.api_key_input.set_value(current_key)

    def _on_apply_api_key(self) -> None:
        """Handle apply API key button click."""
        new_key = self.api_key_input.get_value()

        if not new_key or not new_key.strip():
            self.status_bar.set_message("Please enter an API key", "error")
            return

        # Disable buttons during validation
        self.api_key_apply_button.configure(state="disabled")
        self.api_key_reset_button.configure(state="disabled")
        self.status_bar.set_message("Validating API key...", "info")

        # Validate in background thread
        run_in_thread_with_callback(
            lambda: self.transcription_service.validate_api_key(new_key),
            callback=lambda is_valid: self._on_api_key_validated(new_key, is_valid),
            error_callback=lambda e: self._on_api_key_validation_error(e),
        )

    def _on_api_key_validated(self, api_key: str, is_valid: bool) -> None:
        """
        Callback when API key validation completes.

        Args:
            api_key: The API key that was validated
            is_valid: Whether the key is valid
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_api_key_validated(api_key, is_valid))

    def _handle_api_key_validated(self, api_key: str, is_valid: bool) -> None:
        """
        Handle API key validation result on main thread.

        Args:
            api_key: The API key that was validated
            is_valid: Whether the key is valid
        """
        # Re-enable buttons
        self.api_key_apply_button.configure(state="normal")
        self.api_key_reset_button.configure(state="normal")

        if not is_valid:
            self.status_bar.set_message(
                "Invalid API key. Please check your key and try again.", "error"
            )
            return

        # Save the key using settings manager
        validator = lambda k: True  # Already validated
        if self.settings_manager.update_api_key(api_key, validator):
            # Update the transcription service
            self.transcription_service.update_api_key(api_key)
            self.status_bar.set_message("API key updated successfully!", "success")
        else:
            self.status_bar.set_message("Failed to save API key", "error")

    def _on_api_key_validation_error(self, error: Exception) -> None:
        """
        Callback when API key validation fails with an error.

        Args:
            error: The exception that occurred
        """
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_api_key_validation_error(error))

    def _handle_api_key_validation_error(self, error: Exception) -> None:
        """
        Handle API key validation error on main thread.

        Args:
            error: The exception that occurred
        """
        # Re-enable buttons
        self.api_key_apply_button.configure(state="normal")
        self.api_key_reset_button.configure(state="normal")

        self.status_bar.set_message(f"Validation error: {error}", "error")

    def _on_reset_api_key(self) -> None:
        """Handle reset API key button click."""
        default_key = self.settings_manager.reset_api_key()

        if default_key:
            # Update UI and service
            self.api_key_input.set_value(default_key)
            self.transcription_service.update_api_key(default_key)
            self.status_bar.set_message("API key reset to default", "success")
        else:
            # Clear the input if no default
            self.api_key_input.clear_value()
            self.status_bar.set_message(
                "No default API key found in .env file", "error"
            )
