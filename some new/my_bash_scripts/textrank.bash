#!/bin/bash
screen -dm textrank
screen -S textrank -X stuff "cd /home/hth/extend/TextSum/Single/TexRank
python texrank.py
"