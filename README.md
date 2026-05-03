# vibe-flow

## Plan: make `tone.wav` sound like a real piano

The current pipeline uses `pretty_midi.synthesize()`, which sums sine waves
weighted by note velocity. The output is a clean tone, but it has no piano
timbre because there is no actual piano sample data anywhere in the project.

To get a realistic piano sound, swap the synthesizer for **FluidSynth** driven
by a **SoundFont (`.sf2`)** file. SoundFonts are bundles of recorded
instrument samples; FluidSynth reads them, applies the MIDI note/velocity
events, and renders the result to audio.

### Steps

1. **Install the system library** — FluidSynth is a C library, not a Python
   package:
   ```
   sudo apt install fluidsynth libfluidsynth-dev
   ```
2. **Add the Python wrapper** to the project:
   ```
   uv add pyfluidsynth
   ```
3. **Download a SoundFont.** Two reasonable choices:
   - `FluidR3_GM.sf2` — full General MIDI bank (~140 MB), covers all
     instruments. Available via `apt install fluid-soundfont-gm`, which
     installs to `/usr/share/sounds/sf2/FluidR3_GM.sf2`.
   - A piano-only SoundFont (5–30 MB) such as `SalamanderGrandPiano.sf2`
     for smaller footprint when only piano is needed.
4. **Swap the call** in `main.py`:
   ```python
   audio = pm.fluidsynth(fs=sample_rate, sf2_path="/usr/share/sounds/sf2/FluidR3_GM.sf2")
   ```
   Everything else (clipping, `wave.open()` writer) stays the same.

### Tradeoffs

- **Disk cost.** A full GM SoundFont is ~140 MB. Piano-only fonts are much
  smaller. The `.sf2` is a runtime asset, not a Python dependency, so it
  should live outside the repo (download script or system package).
- **Non-pip dependency.** `libfluidsynth` is installed at the OS level. CI
  and contributor setup need an extra step beyond `uv sync`.
- **No pure-Python alternative.** Any synthesizer that sounds like a piano
  needs sampled piano audio. Algorithmic approaches (additive synthesis,
  physical modeling) get closer than sine waves but still don't match a
  sampled instrument.
