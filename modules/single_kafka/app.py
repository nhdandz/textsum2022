from flask_api import status
from flask_cors import CORS
from flask import Flask,request,Response
from controller import get_input_by_topic,get_input_by_len_and_algor,run_sum
from helper import check_id_mapAlgTypeAI,check_add_optional_value,check_percent_output,check_topic,get_raw_text
import json

# from preprocess import preprocess_memsum

app = Flask(__name__)
CORS(app)


@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/SingleSum', methods=['POST'])
def post():
    result = {}
    with open('db/mapAlgTypeAI.json') as f:
        mapAlgTypeAI = json.load(f)
    if request.method =="POST":
        content = request.get_json() 
        check_add_optional_value(content)
        # print(content)
        if len(content['raw_text']) > 25 and content['raw_text'] is not None:
            text_input = get_raw_text(content['raw_text'],content['file_type'],content['page_from'],content['page_to'])
            # text_file = open("text.txt", "w")
            # n = text_file.write(text_input)
            # text_file.close()
            content['raw_text']  = text_input
            print(content['topic'])
            is_check_id = check_id_mapAlgTypeAI(mapAlgTypeAI,content['id_mapAlgTypeAI'])
            if is_check_id == True :
                is_check_percent= check_percent_output(content['percent_output'])
                if is_check_percent == True:
                    input = get_input_by_topic(content)
                    # print(input)
                    # text_file = open("test_topicr.txt", "w")
                    # n = text_file.write(input[0]['raw_text'])
                    # text_file.close()
                    input = get_input_by_len_and_algor(input)
                    result = run_sum(input)
                    result['original_text'] = content['raw_text'] 
                    # print(result)
                    return result,200
                return result,403
            return result,402
        else:
            return result,404
    return result,405

@app.route('/SingleSum_test', methods=['POST'])
def post3():
    result = {}
    with open('db/mapAlgTypeAI.json') as f:
        mapAlgTypeAI = json.load(f)
    if request.method =="POST":
        content = request.get_json() 
        check_add_optional_value(content)
        if content['raw_text'] is not None:
            is_check_id = check_id_mapAlgTypeAI(mapAlgTypeAI,content['id_mapAlgTypeAI'])
            if is_check_id == True:
                is_check_percent= check_percent_output(content['percent_output'])
                if is_check_percent == True:
                    input = get_input_by_topic(content)
                    input = get_input_by_len_and_algor(input)
                    for data in input:
                        infor_algor = {}
                        for item in mapAlgTypeAI:
                            if item['id'] == data['algor_choose']['algor_id']:
                                infor_algor =item
                        result[data['topic']] = infor_algor
                        print(result)
                    return result,200
                return result,403
            return result,402
        else:
            return result,404
    return result,405

@app.route('/AdminConfig', methods=['POST'])
def post2():
    if request.method =="POST":
        content = request.get_json() 
    return 'None'

app.run(host='0.0.0.0', port=9999,threaded=True)