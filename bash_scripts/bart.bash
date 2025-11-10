#!/bin/bash
screen -dm bart
screen -S bart -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/BART
source ~/miniconda3/etc/profile.d/conda.sh && conda activate BART
python KafkaBart.py
"