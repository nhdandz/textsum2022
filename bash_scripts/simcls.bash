#!/bin/bash
screen -dm simcls
screen -S simcls -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/SimCLS2/simcls-pytorch
source ~/miniconda3/etc/profile.d/conda.sh && conda activate SimCLS2
python SimCLSKafka.py
"