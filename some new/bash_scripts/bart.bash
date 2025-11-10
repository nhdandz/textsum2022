#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm bart
screen -S bart -X stuff "cd $P_PARENT_PATH/TextSum/Single/BART
source $P_PARENT_PATH/envsf/bart/bin/activate
python KafkaBart.py
"