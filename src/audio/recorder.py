"""Audio recording functionality with protocol-based design."""

import queue
import tempfile
import threading
from pathlib import Path
from typing import Optional, Protocol

import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioRecorderProtocol(Protocol):
    """Protocol defining the interface for audio recorders."""

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        ...

    def stop_recording(self) -> Optional[Path]:
        """
        Stop recording and save audio to file.

        Returns:
            Path to the saved audio file, or None if recording failed.
        """
        ...

    def is_recording(self) -> bool:
        """Check if currently recording."""
        ...

    def get_recording_duration(self) -> float:
        """Get the current recording duration in seconds."""
        ...


class AudioRecorder:
    """
    Records audio from the microphone using sounddevice.

    This implementation provides non-blocking recording suitable for GUI applications.
    Audio is recorded in chunks and stored in a queue for processing.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        max_duration: int = 300,
    ) -> None:
        """
        Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for speech recognition)
            channels: Number of audio channels (default: 1 for mono)
            max_duration: Maximum recording duration in seconds (default: 300 = 5 minutes)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration = max_duration

        self._recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._recording_thread: Optional[threading.Thread] = None
        self._frames: list = []
        self._start_time: Optional[float] = None

    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.

        Raises:
            RuntimeError: If already recording or if microphone is not available.
        """
        if self._recording:
            raise RuntimeError("Already recording")

        self._recording = True
        self._frames = []
        self._audio_queue = queue.Queue()

        try:
            # Create input stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                dtype=np.int16,
            )
            self._stream.start()

            # Start recording thread to collect audio chunks
            self._recording_thread = threading.Thread(target=self._record_loop, daemon=True)
            self._recording_thread.start()

            import time

            self._start_time = time.time()

        except Exception as e:
            self._recording = False
            self._stream = None
            raise RuntimeError(f"Failed to start recording: {e}") from e

    def stop_recording(self) -> Optional[Path]:
        """
        Stop recording and save audio to a temporary WAV file.

        Returns:
            Path to the saved audio file, or None if no audio was recorded.

        Raises:
            RuntimeError: If not currently recording.
        """
        if not self._recording:
            raise RuntimeError("Not currently recording")

        self._recording = False

        # Stop the stream
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Wait for recording thread to finish
        if self._recording_thread:
            self._recording_thread.join(timeout=2.0)
            self._recording_thread = None

        # Combine all recorded frames
        if not self._frames:
            return None

        audio_data = np.concatenate(self._frames, axis=0)

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".wav", prefix="recording_"
        )
        temp_path = Path(temp_file.name)
        temp_file.close()

        sf.write(temp_path, audio_data, self.sample_rate, subtype="PCM_16")

        self._start_time = None
        return temp_path

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def get_recording_duration(self) -> float:
        """
        Get the current recording duration in seconds.

        Returns:
            Duration in seconds, or 0.0 if not recording.
        """
        if not self._recording or self._start_time is None:
            return 0.0

        import time

        return time.time() - self._start_time

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags
    ) -> None:
        """
        Callback for audio stream. Called by sounddevice for each audio chunk.

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Stream status flags
        """
        if status:
            print(f"Audio callback status: {status}")

        if self._recording:
            # Put audio data in queue for processing by recording thread
            self._audio_queue.put(indata.copy())

    def _record_loop(self) -> None:
        """Recording loop that runs in a separate thread."""
        import time

        while self._recording:
            # Check if max duration reached
            if self.get_recording_duration() >= self.max_duration:
                print(f"Max recording duration ({self.max_duration}s) reached")
                break

            # Get audio chunks from queue
            try:
                chunk = self._audio_queue.get(timeout=0.1)
                self._frames.append(chunk)
            except queue.Empty:
                continue

        # Signal that recording should stop
        self._recording = False
