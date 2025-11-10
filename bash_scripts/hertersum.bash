#!/bin/bash
screen -dm hertersum
screen -S hertersum -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Multi/HeterSum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate hertersum
python app.py
"