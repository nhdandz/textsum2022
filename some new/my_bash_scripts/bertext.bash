#!/bin/bash
screen -dm bertext
screen -S bertext -X stuff "cd /home/hth/extend/TextSum/Single/BertExt/PreSumm
/venv/bertext/bin/python ./src/sub_single_4.py
"
