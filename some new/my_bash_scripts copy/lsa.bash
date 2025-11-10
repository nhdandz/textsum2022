#!/bin/bash
screen -dm lsa
screen -S lsa -X stuff "cd /app/Single/TexRank
python lsa.py
"