#!/bin/bash
screen -dm textrank
screen -S textrank -X stuff "cd /app/Single/TexRank
python texrank.py
"