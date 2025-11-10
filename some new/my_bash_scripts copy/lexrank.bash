#!/bin/bash
screen -dm lexrank
screen -S lexrank -X stuff "cd /app/Single/TexRank
python lexrank.py
"