#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm simcls
screen -S simcls -X stuff "cd $P_PARENT_PATH/TextSum/Single/SimCLS2/simcls-pytorch
source $P_PARENT_PATH/envsf/bart/bin/activate
python SimCLSKafka.py
"