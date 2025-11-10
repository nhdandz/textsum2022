#!/bin/bash
screen -dm multibart
screen -S multibart -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/pegasus-xsum
source ~/miniconda3/etc/profile.d/conda.sh && conda activate test
python MultiBartKafka.py
"