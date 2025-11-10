#!/bin/bash
screen -dm lsa
screen -S lsa -X stuff "cd /home/hth/extend/TextSum/Single/TexRank
python lsa.py
"