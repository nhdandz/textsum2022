#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm longbart
screen -S longbart -X stuff "cd /home/khmt/textsum/TextSum/Single/pegasus-xsum
source /home/khmt/textsum/envsf/bart/bin/activate
python LongBartKafka.py
"