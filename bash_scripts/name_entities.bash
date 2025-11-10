#!/bin/bash
screen -dm name_entities
screen -S name_entities -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/NER
source ~/miniconda3/etc/profile.d/conda.sh && conda activate NERnltk
python app.py
"