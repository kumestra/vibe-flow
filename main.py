import wave

import numpy as np
import pretty_midi


def generate_midi(
    path: str = "tone.mid", duration: float = 10.0
) -> pretty_midi.PrettyMIDI:
    pm = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

    a4 = pretty_midi.note_name_to_number("A4")  # 440 Hz
    piano.notes.append(
        pretty_midi.Note(velocity=100, pitch=a4, start=0.0, end=duration)
    )

    pm.instruments.append(piano)
    pm.write(path)
    return pm


def synthesize_to_wav(
    pm: pretty_midi.PrettyMIDI,
    path: str = "tone.wav",
    sample_rate: int = 44100,
) -> None:
    audio = pm.synthesize(fs=sample_rate)
    samples = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)

    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(samples.tobytes())


def main():
    pm = generate_midi()
    synthesize_to_wav(pm)
    print("Wrote tone.mid (A4 / 440 Hz, 10s, Acoustic Grand Piano)")
    print("Wrote tone.wav (synthesized via pretty_midi sine-wave bank)")


if __name__ == "__main__":
    main()
