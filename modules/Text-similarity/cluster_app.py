from flask_api import status
from flask_cors import CORS
from flask import Flask,request, redirect, url_for
import pathlib
import random
import time
ar = [0,1]
app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())

@app.route('/')
def GetStatusService():
    return 'ok'

global is_status
is_status = True
from infer import text_cluster
@app.route('/TextClustering', methods=['POST'])
def post2():
    if request.method =="POST":
        content = request.get_json()
        result = {}
        result['clusters'] = []
        print("start")
        if content['list_doc'] is not None:
            # if random.choice(ar) == 1: 
            #     return redirect("http://192.168.213.13:9450/TextClustering", code=307)
            # else:
                tic= time.time()

                result['clusters'] = text_cluster(content['list_doc'], len(content['list_doc']))
                print(result)
                tac = time.time()
                print(tac - tic)
                return  result
        return result
    return None

@app.route('/change_status', methods=['POST'])
def post3():
    if request.method =="POST":
        content = request.get_json()
        response_change_status ={}
        response_change_status['result'] = False
        global is_status
        try:
            if content['status'] == True and is_status == False:
                # 
                is_status = True
            elif content['status'] == False and is_status == True:
                # 
                is_status = False
            else:
                print('ok')
            response_change_status['result'] = True
        except:
            response_change_status['result'] = False
    return response_change_status

@app.route('/get_status')
def get():
    global is_status
    response_status ={}
    response_status['status'] = is_status
    return response_status


app.run(host='0.0.0.0', port=9400,threaded=True)
