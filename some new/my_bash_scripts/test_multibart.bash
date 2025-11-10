screen -dm bart
screen -S bart -X stuff "cd /home/hth/extend/TextSum/Single/pegasus-xsum/
 python MultiBartKafka.py
"