#!/bin/bash
screen -dm memsum
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -S memsum -X stuff "cd $P_PARENT_PATH/TextSum/Single/MemSum
source $P_PARENT_PATH/envs/memsum_envs/bin/activate && python sub_single_16.py
"
