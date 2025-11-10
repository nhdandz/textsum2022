#!/bin/bash
screen -dm multi_kafka
screen -S multi_kafka -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/root_kafka
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python multi_kafka.py
"