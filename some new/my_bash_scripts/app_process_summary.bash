#!/bin/bash
screen -dm app_process_summary
screen -S app_process_summary -X stuff "cd /home/hth/extend/TextSum/modules/single_kafka
/venv/kafka/bin/python app_process.py
"
