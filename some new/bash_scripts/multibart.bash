#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm multibart
screen -S multibart -X stuff "cd $P_PARENT_PATH/TextSum/Single/pegasus-xsum
source $P_PARENT_PATH/envsf/bart/bin/activate
python MultiBartKafka.py
"