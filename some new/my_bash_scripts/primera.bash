#!/bin/bash
screen -dm primera
screen -S primera -X stuff "cd /home/hth/extend/TextSum/Multi/primera
source /home/hth/envs/primera_envs/bin/activate && python sub_single_21.py
"
