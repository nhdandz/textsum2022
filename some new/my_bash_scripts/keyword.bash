#!/bin/bash
screen -dm keyword
screen -S keyword -X stuff "cd /home/hth/extend/TextSum/modules/Key-Bert
/venv/keyword/bin/python app2.py
"