#!/bin/bash
screen -dm clustering
screen -S clustering -X stuff "cd /home/hth/extend/TextSum/modules/Text-similarity
/venv/clustering/bin/python cluster_app.py
"

