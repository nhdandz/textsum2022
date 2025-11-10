#!/bin/bash
screen -dm textsum_fe
screen -S textsum_fe -X stuff "cd /home/khmt/Desktop/edms_sum/ui_edms
npm start
"