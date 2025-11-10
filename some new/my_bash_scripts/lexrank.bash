#!/bin/bash
screen -dm lexrank
screen -S lexrank -X stuff "cd /home/hth/extend/TextSum/Single/TexRank
python lexrank.py
"