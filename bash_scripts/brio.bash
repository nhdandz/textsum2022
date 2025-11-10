#!/bin/bash
screen -dm brio
screen -S brio -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate test
python BrioKafka.py
"