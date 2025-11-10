screen -dm bart
screen -S bart -X stuff "cd /app/Single/pegasus-xsum/
ENV PATH="/venv/bart/bin:$PATH"
cd /app/Single/pegasus-xsum && python MultiBartKafka.py
"