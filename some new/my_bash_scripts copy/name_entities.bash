#!/bin/bash
screen -dm name_entities
screen -S name_entities -X stuff "cd /app/modules/NER
/venv/entities/bin/python app.py
"