#!/bin/bash
screen -dm longbart2
screen -S longbart2 -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate BART
python LongBartKafka.py
"