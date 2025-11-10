#!/bin/bash
current_directory=$(pwd)
PARENT_PATH="$(dirname "$current_directory")"
P_PARENT_PATH="$(dirname "$PARENT_PATH")"
screen -dm name_entities
screen -S name_entities -X stuff "cd $P_PARENT_PATH/TextSum/modules/NER
source $P_PARENT_PATH/envsf/entities/bin/activate
python app.py
"