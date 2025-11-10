#!/bin/bash
screen -dm single_kafka
screen -S single_kafka -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python single_root.py
"
