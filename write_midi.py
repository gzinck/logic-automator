from midiutil import MIDIFile
import sys
import json


def write_midi(notes, path):
    track = 0
    channel = 0
    time = 0  # In beats
    duration = 0.5  # In beats
    tempo = 90  # In BPM
    volume = 80  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(notes):
        if i == len(notes) - 1:
            duration = 6
        MyMIDI.addNote(track, channel, pitch, time + i / 2, duration, volume)

    with open(path, "wb") as output_file:
        MyMIDI.writeFile(output_file)


# If we run this script on the command line
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: write_midi.py <notes_array> <output_name>")
        print(
            "For <notes_array>, it should be a quoted string like '[0, 4, 5]' where 0 is the MIDI note number 0"
        )
        sys.exit(1)

    notes_array = json.loads(sys.argv[1])
    output_name = sys.argv[2]

    write_midi(notes_array, output_name)
