#!bin/bash
for session in $(screen -ls | grep -o '[0-9]*\.app_process_summary'); do screen -S "${session}" -X quit; done
