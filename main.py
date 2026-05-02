import wave

import numpy as np


def generate_tone(
    path: str = "tone.wav",
    frequency: float = 440.0,
    duration: float = 10.0,
    sample_rate: int = 44100,
    amplitude: float = 0.5,
) -> None:
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    waveform = amplitude * np.sin(2 * np.pi * frequency * t)
    samples = (waveform * 32767).astype(np.int16)

    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(samples.tobytes())


def main():
    generate_tone()
    print("Wrote tone.wav (440 Hz, 10s, mono, 44.1 kHz, 16-bit PCM)")


if __name__ == "__main__":
    main()
