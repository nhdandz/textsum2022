from queue import Queue
import requests
import time 
import os 
from flask import Flask,jsonify
from flask import request
from flask_cors import CORS
import init
import texrank
import lexrank
import lsa
import multi_lexrank
import multi_texrank
import multi_lsa


app = Flask(__name__)
CORS(app)

def start_service(bash_script):
    try:
        os.system(f"bash {bash_script}")
    except:
        return False
    return True

def turn_off_service(pid):
    import signal
    # try:
    print(f"kill pid: {pid}")
    os.kill(int(pid), signal.SIGKILL)
    # except:
    #     # failed kill
    #     return  False
    return  True

@app.route('/change_status_multextrank', methods=['POST'])
def post():
    content = request.get_json()
    status = content["status"]
    
    # kill
    if status == False:
        pid = init.multi_textrank_pid
        status = turn_off_service(pid)
        return {"status":status}

    # start service
    status = start_service("/home/user01/tupk/test_kafka/TexRank/turn_on_multextrank.bash")
    return {"status":status}

app.run(host='0.0.0.0', port=5678)

if __name__ =="__main__":
    print(init.lsa_pid)