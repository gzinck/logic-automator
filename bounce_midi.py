# Supports python 3.X on macOS
# Authored by Graeme Zinck (graemezinck.ca)
# 23 April 2021
#
# Takes a midi file and bounces it to MP3 using an empty logic project.
# Can use a custom instrument and preset.

import logic
import sys
import json


def bounce_midi(project_path, midi_path, output_name, instrument=None, preset=None):
    logic.open(project_path)
    logic.importMidi(midi_path)
    logic.selectLastTrack()

    if instrument:
        logic.selectInstrument(instrument)
    if preset:
        logic.selectPresetSound(preset)

    logic.bounce(output_name)
    logic.deleteLastTrack()
    logic.close()


# If we run this script on the command line
if __name__ == "__main__":
    if len(sys.argv) not in [4, 6]:
        print(
            "Usage: bounce_midi.py <path_to_logic_project> <path_to_midi_file> <output_name> (<instrument> (<preset>))"
        )
        print(
            'For <instrument>, it should be a quoted string like \'["AU Instruments", "Native Instruments", "Kontakt", "Stereo"]\''
        )
        print(
            "The preset should be a preset you create and add to your library for the instrument"
        )
        sys.exit(1)

    project_path = sys.argv[1]
    midi_path = sys.argv[2]
    output_name = sys.argv[3]
    instrument = None if len(sys.argv) < 5 else json.loads(sys.argv[4])
    preset = None if len(sys.argv) < 6 else sys.argv[5]

    bounce_midi(project_path, midi_path, output_name, instrument, preset)
