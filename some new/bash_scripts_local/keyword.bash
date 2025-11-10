#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm keyword
screen -S keyword -X stuff "cd /home/khmt/textsum/TextSum/modules/Key-Bert
source /home/khmt/textsum/envsf/keyword/bin/activate
python app2.py
"