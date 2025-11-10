#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm multi_kafka
screen -S multi_kafka -X stuff "cd $P_PARENT_PATH/TextSum/modules/root_kafka
source $P_PARENT_PATH/envsf/kafka/bin/activate
python multi_kafka.py
"