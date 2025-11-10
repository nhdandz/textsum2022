#!/bin/bash
screen -dm single_kafka
screen -S single_kafka -X stuff "cd /app/modules/single_kafka
/venv/singleroot/bin/python single_root.py
"
