#!/bin/bash
screen -dm textrank
screen -S textrank -X stuff "cd /home/khmt/textsum/TextSum/Single/TexRank
source /home/khmt/textsum/envsf/kafka/bin/activate
python texrank.py
"