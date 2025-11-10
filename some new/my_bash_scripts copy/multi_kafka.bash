#!/bin/bash
screen -dm multi_kafka
screen -S multi_kafka -X stuff "cd /app/modules/root_kafka
/venv/kafka/bin/python multi_kafka.py
"