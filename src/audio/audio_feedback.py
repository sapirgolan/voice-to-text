"""Audio feedback for user interactions (beeps)."""

import threading
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd


class AudioFeedback:
    """
    Provides audio feedback for user interactions.

    Plays short beep sounds to indicate start/stop of recording.
    """

    def __init__(self, sample_rate: int = 44100) -> None:
        """
        Initialize audio feedback system.

        Args:
            sample_rate: Sample rate for audio playback (default: 44100 Hz)
        """
        self.sample_rate = sample_rate
        self._playing = False

    def play_start_beep(self) -> None:
        """Play a beep sound to indicate recording has started."""
        # High pitch, short beep
        self._play_beep(frequency=800, duration=0.1)

    def play_stop_beep(self) -> None:
        """Play a beep sound to indicate recording has stopped."""
        # Lower pitch, slightly longer beep
        self._play_beep(frequency=600, duration=0.15)

    def play_error_beep(self) -> None:
        """Play a beep sound to indicate an error."""
        # Lower pitch, longer beep
        self._play_beep(frequency=400, duration=0.2)

    def _play_beep(self, frequency: int, duration: float) -> None:
        """
        Play a simple sine wave beep.

        Args:
            frequency: Frequency of the beep in Hz
            duration: Duration of the beep in seconds
        """
        if self._playing:
            return

        self._playing = True

        # Run in separate thread to avoid blocking
        thread = threading.Thread(
            target=self._play_beep_sync, args=(frequency, duration), daemon=True
        )
        thread.start()

    def _play_beep_sync(self, frequency: int, duration: float) -> None:
        """
        Synchronously play a beep sound.

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
        """
        try:
            # Generate sine wave
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            wave = np.sin(frequency * 2 * np.pi * t)

            # Apply fade in/out to avoid clicks
            fade_samples = int(self.sample_rate * 0.01)  # 10ms fade
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)

            wave[:fade_samples] *= fade_in
            wave[-fade_samples:] *= fade_out

            # Normalize and convert to appropriate format
            wave = wave.astype(np.float32) * 0.3  # Reduce volume to 30%

            # Play the sound
            sd.play(wave, self.sample_rate)
            sd.wait()

        except Exception as e:
            print(f"Failed to play beep: {e}")
        finally:
            self._playing = False

    @staticmethod
    def generate_beep_files(output_dir: Path) -> None:
        """
        Generate beep audio files for distribution.

        This method creates WAV files that can be packaged with the application.

        Args:
            output_dir: Directory to save the generated beep files
        """
        import soundfile as sf

        output_dir.mkdir(parents=True, exist_ok=True)

        sample_rate = 44100

        # Generate start beep (800 Hz, 0.1s)
        t_start = np.linspace(0, 0.1, int(sample_rate * 0.1), False)
        start_wave = np.sin(800 * 2 * np.pi * t_start).astype(np.float32) * 0.3
        sf.write(output_dir / "start_beep.wav", start_wave, sample_rate)

        # Generate stop beep (600 Hz, 0.15s)
        t_stop = np.linspace(0, 0.15, int(sample_rate * 0.15), False)
        stop_wave = np.sin(600 * 2 * np.pi * t_stop).astype(np.float32) * 0.3
        sf.write(output_dir / "stop_beep.wav", stop_wave, sample_rate)

        # Generate error beep (400 Hz, 0.2s)
        t_error = np.linspace(0, 0.2, int(sample_rate * 0.2), False)
        error_wave = np.sin(400 * 2 * np.pi * t_error).astype(np.float32) * 0.3
        sf.write(output_dir / "error_beep.wav", error_wave, sample_rate)
