#!/bin/bash
screen -dm textsum_be
screen -S textsum_be -X stuff "cd /home/khmt/Desktop/edms_sum/edms
npm start
"