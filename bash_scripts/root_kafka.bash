#!/bin/bash
screen -dm root_kafka
screen -S root_kafka -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/root_kafka
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python root_kafka.py 
"