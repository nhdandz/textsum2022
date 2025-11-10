#!/bin/bash
# Tạo một screen và chạy lệnh trong screen đầu tiên
screen -dmS screen1 bash -c 'cd /app/Single/pegasus-xsum && python LongBartKafka.py"'

# Tạo một screen và chạy lệnh trong screen thứ hai
screen -dmS screen2 bash -c 'cd /app/Single/pegasus-xsum && python MultiBartKafka.py'

# Giữ container chạy bằng cách không thoát khỏi shell script
exec bash