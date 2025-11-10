#!/bin/bash
screen -dm memsum
screen -S memsum -X stuff "cd /home/hth/extend/TextSum/Single/MemSum
source /home/hth/envs/memsum_envs/bin/activate && python sub_single_16.py
"
