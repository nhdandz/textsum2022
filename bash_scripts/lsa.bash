#!/bin/bash
screen -dm lsa
screen -S lsa -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/TexRank
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python lsa.py
"