#!/bin/bash
screen -dm primera
screen -S primera -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Multi/primera
source /home/hth/envs/primera_envs/bin/activate && python sub_single_21.py
"
