#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"

screen -dm algo_control
screen -S algo_control -X stuff "cd $P_PARENT_PATH/TextSum/modules/algorithm_control
source $P_PARENT_PATH/envsf/kafka/bin/activate 
python algo_control_app.py 
"