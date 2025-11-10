#!/bin/bash
screen -dm algo_control
screen -S algo_control -X stuff "cd /home/hth/extend/TextSum/modules/algorithm_control
/venv/kafka/bin/python algo_control_app.py
"