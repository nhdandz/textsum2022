#!/bin/bash
screen -dm keyword
screen -S keyword -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Key-Bert
source ~/miniconda3/etc/profile.d/conda.sh && conda activate keyBert
python app2.py
"