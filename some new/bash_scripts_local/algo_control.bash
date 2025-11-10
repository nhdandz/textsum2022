#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"

screen -dm algo_control
screen -S algo_control -X stuff "cd /home/khmt/textsum/TextSum/modules/algorithm_control
source /home/khmt/textsum/envsf/kafka/bin/activate 
python algo_control_app.py 
"
