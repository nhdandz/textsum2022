#!/bin/bash
screen -dm longbart
screen -S longbart -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum
/venv/bart/bin/python LongBartKafka.py
"