#!/bin/bash
screen -dm hertersum
screen -S hertersum -X stuff "cd /app/home/hth/extend/TextSum/Multi/HeterSum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate hertersum
python app.py
"