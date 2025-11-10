#!/bin/bash
screen -dm multibart
screen -S multibart -X stuff "cd /app/Single/pegasus-xsum
/venv/bart/bin/python MultiBartKafka.py
"