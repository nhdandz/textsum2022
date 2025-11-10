#!/bin/bash
screen -dm clustering
screen -S clustering -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Text-similarity
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python cluster_app.py
"

