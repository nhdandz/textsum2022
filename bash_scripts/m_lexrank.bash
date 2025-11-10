#!/bin/bash
screen -dm m_lexrank
screen -S m_lexrank -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Multi/MulTexRank
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python multi_lexrank.py
"