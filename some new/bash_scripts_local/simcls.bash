#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm simcls
screen -S simcls -X stuff "cd /home/khmt/textsum/TextSum/Single/SimCLS2/simcls-pytorch
source /home/khmt/textsum/envsf/bart/bin/activate
python SimCLSKafka.py
"