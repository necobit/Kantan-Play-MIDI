# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based MIDI controller project called "Kantan-Play-MIDI" (かんたんプレイMIDI) designed to control a hardware gadget called "かんぷれ" (Kanpure) by converting JSON musical notation data into MIDI output commands.

## Key Architecture

### Current Structure
- `MIDI.json`: MIDI note mapping configuration
  - slot: MIDI notes 24-31 (8 slots)
  - notes: MIDI notes 60-71 (12 musical degrees)
  - modifier1/2/3: MIDI notes 52-59 (8 modifiers each)
- `README.md`: Japanese documentation explaining the JSON format and playing logic

### Expected Implementation
The project requires a Python script that:
1. Reads JSON input with musical sequences
2. Maps musical degrees (1, 2b, 2, 3b, 3, 4, 5b, 5, 6b, 6, 7b, 7) to MIDI notes
3. Sends MIDI commands via selectable MIDI interface
4. Simulates button presses using MIDI note on/off messages
5. Controls timing based on BPM (4 degree button presses = 1 beat)

### JSON Input Format
```json
{
  "slot": 1,
  "tempo": 120,
  "notes": [
    {
      "degree": "1",
      "modifier1": 0,
      "modifier2": 0,
      "modifier3": 0
    }
  ]
}
```

## Development Commands

Since this project is not yet implemented, typical commands would be:
- Install MIDI library: `pip install python-rtmidi` or `pip install mido`
- Run the main script: `python main.py input.json` (once created)

## Important Notes

- All documentation is in Japanese
- The project simulates physical button presses on hardware
- Modifiers are pressed simultaneously with degree notes
- Slot selection sends a 50ms MIDI note pulse
- Channel 1 is used for all MIDI communication