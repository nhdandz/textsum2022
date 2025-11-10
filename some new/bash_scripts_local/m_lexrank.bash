#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm m_lexrank
screen -S m_lexrank -X stuff "cd /home/khmt/textsum/TextSum/Multi/MulTexRank
source /home/khmt/textsum/envsf/kafka/bin/activate
python multi_lexrank.py
"