#!/bin/bash
screen -dm lexrank
screen -S lexrank -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/TexRank
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python lexrank.py
"