#!/bin/bash
screen -dm single_kafka
screen -S single_kafka -X stuff "cd /home/hth/extend/TextSum/modules/single_kafka
/venv/singleroot/bin/python single_root.py
"
