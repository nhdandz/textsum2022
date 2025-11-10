#!/bin/bash
screen -dm root_kafka
screen -S root_kafka -X stuff "cd /app/modules/root_kafka
/venv/kafka/bin/python root_kafka.py 
"