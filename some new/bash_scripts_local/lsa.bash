#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm lsa
screen -S lsa -X stuff "cd /home/khmt/textsum/TextSum/Single/TexRank
source /home/khmt/textsum/envsf/kafka/bin/activate
python lsa.py
"