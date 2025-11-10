#!/bin/bash
screen -dm longbart
screen -S longbart -X stuff "cd /app/Single/pegasus-xsum
/venv/bart/bin/python LongBartKafka.py
"