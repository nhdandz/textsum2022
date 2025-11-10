#!/bin/bash
screen -dm m_lexrank
screen -S m_lexrank -X stuff "cd /app/Multi/MulTexRank
python multi_lexrank.py
"