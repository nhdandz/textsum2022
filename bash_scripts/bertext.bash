#!/bin/bash
screen -dm bertext
screen -S bertext -X stuff "cd /home/nhdandz/Documents/tupk/textsum2022/modules/Single/BertExt/PreSumm
source /home/hth/envs/presum_envs/bin/activate && python ./src/sub_single_4.py
"
