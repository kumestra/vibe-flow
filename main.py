import pretty_midi


def generate_midi(path: str = "tone.mid", duration: float = 10.0) -> None:
    pm = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

    a4 = pretty_midi.note_name_to_number("A4")  # 440 Hz
    piano.notes.append(
        pretty_midi.Note(velocity=100, pitch=a4, start=0.0, end=duration)
    )

    pm.instruments.append(piano)
    pm.write(path)


def main():
    generate_midi()
    print("Wrote tone.mid (A4 / 440 Hz, 10s, Acoustic Grand Piano)")


if __name__ == "__main__":
    main()
