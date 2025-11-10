#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm root_kafka
screen -S root_kafka -X stuff "cd /home/khmt/textsum/TextSum/modules/root_kafka
source /home/khmt/textsum/envsf/kafka/bin/activate
python root_kafka.py 
"