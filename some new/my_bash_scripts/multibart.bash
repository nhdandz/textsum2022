#!/bin/bash
screen -dm multibart
screen -S multibart -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum
/venv/bart/bin/python MultiBartKafka.py
"