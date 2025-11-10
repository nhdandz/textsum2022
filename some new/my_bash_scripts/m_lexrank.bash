#!/bin/bash
screen -dm m_lexrank
screen -S m_lexrank -X stuff "cd /home/hth/extend/TextSum/Multi/MulTexRank
python multi_lexrank.py
"