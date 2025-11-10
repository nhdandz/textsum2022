#!/bin/bash
screen -dm memsum
screen -S memsum -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/MemSum
source /home/hth/envs/memsum_envs/bin/activate && python sub_single_16.py
"
