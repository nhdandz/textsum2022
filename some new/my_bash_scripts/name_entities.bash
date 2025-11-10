#!/bin/bash
screen -dm name_entities
screen -S name_entities -X stuff "cd /home/hth/extend/TextSum/modules/NER
/venv/entities/bin/python app.py
"