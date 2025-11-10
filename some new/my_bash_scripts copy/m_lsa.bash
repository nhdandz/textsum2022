#!/bin/bash
screen -dm m_lsa
screen -S m_lsa -X stuff "cd /app/Multi/MulTexRank
python multi_lsa.py
"