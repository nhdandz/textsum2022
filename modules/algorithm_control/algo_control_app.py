from flask_api import status
from flask import Flask,jsonify
from flask import request, redirect, url_for
from flask_cors import CORS
import logging
logging.basicConfig(level= logging.INFO)
import helpers
import json
import controller
import init 
import bson
app = Flask(__name__)
CORS(app)


@app.route('/')
def GetStatusService():
    return "start",status.HTTP_200_OK



@app.route("/change_status", methods=['POST'])
def change():
    content = request.get_json()  
    code = helpers.check_valid_input(content)
    if code != True:
        return {"text": "Dau vao chua dung format", "result":"fail!"}
    status = controller.change_status(content)
    if not status:
        return {"text": "Khong the update thuat toan", "result":"fail!"}
    return {"text": "Thay doi trang thai thuat toan thanh cong", "result":"success!"}



@app.route("/get_detail_algo", methods=['POST'])
def get_detail_algo():
    content = request.get_json()
    id_mapAI = content["id_mapAI"]
    topic, algo_id = init.get_detail_algo(id_mapAI)
    print(topic)
    return {"topic":topic, "algo_id":algo_id}


# init.Initialize()
app.run(host='0.0.0.0', port=6789)
