#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm m_lsa
screen -S m_lsa -X stuff "cd $P_PARENT_PATH/TextSum/Multi/MulTexRank
source $P_PARENT_PATH/envsf/kafka/bin/activate
python multi_lsa.py
"