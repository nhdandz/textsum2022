#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm app_process_summary
screen -S app_process_summary -X stuff "cd $P_PARENT_PATH/TextSum/modules/single_kafka
source $P_PARENT_PATH/envsf/single_root_envs/bin/activate
python app_process.py
"
