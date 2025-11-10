#!/bin/bash
screen -dm longbart2
screen -S longbart2 -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate test
python LongBartKafka.py
"