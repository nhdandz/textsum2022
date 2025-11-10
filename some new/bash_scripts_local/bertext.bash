#!/bin/bash
screen -dm bertext
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -S bertext -X stuff "cd /home/khmt/textsum/TextSum/Single/BertExt/PreSumm
source /home/khmt/textsum/envsf/bertext/bin/activate
python ./src/sub_single_4.py
"
