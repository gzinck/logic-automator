# Supports python 3.X on macOS
# Authored by Graeme Zinck (graemezinck.ca)
# 22 April 2021

# To run (for Graeme): python3 transpose.py "/Volumes/Graeme's MacExtender/Documents/Music/2021/research-series/research-demo-02/research-demo-02.logicx" 1

import sys
import time
import atomacos
import subprocess
import logic

# Make sure we're given a logic file and a transposition interval.
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('Usage: transpose.py <path_to_logic_project> <number_of_transpositions> (<file_prefix>)')
    sys.exit(1)

# Constants
project = sys.argv[1]
n_transpositions = int(sys.argv[2])

file_prefix = project.split('/')[-1].replace('.logicx', '')
if len(sys.argv) == 4:
    file_prefix = sys.argv[3]

logic.open(project)
for i in range(0, n_transpositions):
    filename = f'{file_prefix}-{i}'
    print('********************')
    print(f'Starting file {filename}')
    print('********************')
    logic.selectAllRegions()
    logic.transpose(i)
    logic.bounce(filename)
logic.close()
