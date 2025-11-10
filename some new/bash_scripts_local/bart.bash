#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm bart
screen -S bart -X stuff "cd /home/khmt/textsum/TextSum/Single/BART
source /home/khmt/textsum/envsf/bart/bin/activate
python KafkaBart.py
"