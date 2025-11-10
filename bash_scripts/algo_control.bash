#!/bin/bash
screen -dm algo_control
screen -S algo_control -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/algorithm_control
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python algo_control_app.py 
"