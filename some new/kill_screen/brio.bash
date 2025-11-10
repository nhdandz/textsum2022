#!bin/bash
for session in $(screen -ls | grep -o '[0-9]*\.brio'); do screen -S "${session}" -X quit; done
