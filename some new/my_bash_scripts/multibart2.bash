#!/bin/bash
screen -dm multibart2
screen -S multibart2 -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate BART
python MultiBartKafka.py
"