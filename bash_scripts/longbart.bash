#!/bin/bash
screen -dm longbart
screen -S longbart -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate test
python LongBartKafka.py
"