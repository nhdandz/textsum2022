#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm lsa
screen -S lsa -X stuff "cd $P_PARENT_PATH/TextSum/Single/TexRank
source $P_PARENT_PATH/envsf/kafka/bin/activate
python lsa.py
"