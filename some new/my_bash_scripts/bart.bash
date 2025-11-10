#!/bin/bash
screen -dm bart
screen -S bart -X stuff "cd /home/hth/extend/TextSum/Single/BART
/venv/bart/bin/python KafkaBart.py
"