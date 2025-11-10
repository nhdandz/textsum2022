#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm primera
screen -S primera -X stuff "cd $P_PARENT_PATH/TextSum/Multi/primera
source $P_PARENT_PATH/envs/primera_envs/bin/activate && python sub_single_21.py
"
