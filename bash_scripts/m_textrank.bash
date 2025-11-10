#!/bin/bash
screen -dm m_textrank
screen -S m_textrank -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Multi/MulTexRank
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python multi_texrank.py
"