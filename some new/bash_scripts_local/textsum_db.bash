#!/bin/bash
screen -dm textsum_db
screen -S textsum_db -X stuff "cd /home/khmt/Desktop/edms_sum/edms
docker compose up
"