#!/bin/bash
screen -dm clustering
screen -S clustering -X stuff "cd /home/khmt/textsum/TextSum/modules/Text-similarity
source /home/khmt/textsum/envsf/clustering/bin/activate
python cluster_app.py
"

