# Logic Automator

This has scripts for automating various tasks in Logic Pro X.

## Setup

- Make sure you have `python3` installed and sourced in your `.zprofile` 
  file (if you are using `zsh` as your shell).
- Make sure Xcode is installed fully.
- Run `pip install pyobjc atomacos`

## Running

- **Transpose**: to transpose a song and bounce it into every single key,
  run the following command. It exports to MP3 with default settings and
  overwrites existing files, if any.
```
python3 transpose.py <path_to_logic_project> 12 <name_of_output_files>
```

## Acknowledgements

Most of the code for bouncing files is adapted from
[psobot's solution](https://gist.github.com/psobot/81635e6cbc933b7e8862),
but it is updated to work with Python 3 and newer versions of Logic.
