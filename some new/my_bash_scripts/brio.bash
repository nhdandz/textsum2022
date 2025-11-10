#!/bin/bash
screen -dm brio
screen -S brio -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate BART
python BrioKafka.py
"