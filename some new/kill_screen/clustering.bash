#!bin/bash
for session in $(screen -ls | grep -o '[0-9]*\.clustering'); do screen -S "${session}" -X quit; done
for session in $(screen -ls | grep -o '[0-9]*\.clustering2'); do screen -S "${session}" -X quit; done
