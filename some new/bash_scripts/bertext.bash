#!/bin/bash
screen -dm bertext
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -S bertext -X stuff "cd $P_PARENT_PATH/TextSum/Single/BertExt/PreSumm
source $P_PARENT_PATH/envsf/bertext/bin/activate
python ./src/sub_single_4.py
"
