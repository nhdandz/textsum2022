#!/bin/bash
screen -dm bart
screen -S bart -X stuff "cd /app/Single/BART
/venv/bart/bin/python KafkaBart.py
"