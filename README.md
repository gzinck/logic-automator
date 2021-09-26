# Logic Automator

This has scripts for automating various tasks in Logic Pro X.

## Setup

-   Make sure you have `python3` installed and sourced in your `.zprofile`
    file (if you are using `zsh` as your shell).
-   Make sure Xcode is installed fully.
-   Run `pip install pyobjc atomacos`

## Running

-   **Transpose**: to transpose a song and bounce it by N semitones,
    run the following command. It exports to MP3 with default settings and
    overwrites existing files, if any.

```sh
python3 transpose.py <path_to_logic_project> <transpose_by> <output_name>
# Example: python3 transpose.py '/path/to/some\ project.logicx' 3 transposed_output
```

-   **Write MIDI**: to create a midi file with a custom sequence of notes,
    as specified by their MIDI note numbers, use the following command:

```sh
python3 write_midi.py <notes_array> <output_name>
# Example: python3 write_midi.py '[0, 4, 5]' '/path/to/some\ midi.mid'
```

-   **Bounce MIDI**: to export a midi file as an MP3 file, use this:

```sh
python3 bounce_midi.py \
    <path_to_logic_project> \
    <path_to_midi_file> \
    <output_name> \
    (<instrument> (<preset>))
# Example: python3 bounce_midi.py \
#   '/path/to/some\ project.logicx' \
#   '/path/to/some\ midi.mid' \
#   'out' \
#   '["AU Instruments", "Native Instruments", "Kontakt", "Stereo"]' \
#   'my_preset'
```

## Development

Unfortunately, the package this depends on (atomacos) has a number of major issues
and Logic's interface keeps changing to make this code obsolete. Since this script
has fulfilled my needs to date, I am leaving things here. If you have fixes that
crop up moving forward, feel free to submit a pull request.

Known issues:

-   When importing a MIDI file, atomacos sometimes replaces slashes with question
    marks and crashes. This is not always the case, but it occasionally occurs.
    This is a bug in atomacos, not this. A workaround is necessary in the future.
-   Sometimes the bounce menu does not appear.

### Linting

First, set up the git hooks:

```sh
git config --local core.hooksPath .githooks/
```

Then, install dev dependencies so you can lint your files as you go:

```sh
pip install black
```

## Acknowledgements

Most of the code for bouncing files is adapted from
[psobot's solution](https://gist.github.com/psobot/81635e6cbc933b7e8862),
but it is updated to work with Python 3 and newer versions of Logic.
