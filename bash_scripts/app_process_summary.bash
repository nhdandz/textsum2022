#!/bin/bash
screen -dm app_process_summary
screen -S app_process_summary -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka
source ~/miniconda3/etc/profile.d/conda.sh && conda activate textsum
python app_process.py
"