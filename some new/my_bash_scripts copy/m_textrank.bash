#!/bin/bash
screen -dm m_textrank
screen -S m_textrank -X stuff "cd /app/Multi/MulTexRank
python multi_lexrank.py
"