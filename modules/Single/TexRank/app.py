from algtm import lexrank_extract_sum, lsa_extract_sum, luhn_text_sum, kl_extract_sum
from flask_api import status
from flask_cors import CORS
from flask import Flask,request
from prep import *
app = Flask(__name__)
CORS(app)
from counter import count_sentences, short_count_sentences
status = True
@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/TexRank', methods=['POST'])
def post():
    if request.method =="POST":
        content = request.get_json()
        result = {}
        result['Summary'] = ''
        if content['text'] is not None:
            if content['percent_output'] is not None:
                per = content['percent_output']
            else:
                per = 0.1
            summary =  luhn_text_sum(content['text'], short_count_sentences(content['text'], per))
            result['Summary'] = summary
            print(result)
            return  result
        return result
    return None

@app.route('/MultiTexRank', methods=['POST', 'GET'])
def post4():
    if request.method =="POST":
        content = request.get_json()
        print(content)
        result = {}
        result['result'] = ''
        if content['list_doc'] is not None:
            texts = prep(content['list_doc'])
            print(texts)
            extracted_sen =luhn_text_sum(texts, count_sentences(texts))
            summary = extracted_sen
            summary = summary.replace('\"', '"')
            summary = summary.replace("\'", "'")
            summary = summary.replace("\"", '"')
            summary = summary.replace("\\n", '')
            summary = summary.replace("\\", '')
            summary = summary.replace("||||", '')
            summary = summary.replace("  ", ' ')

            result['result'] = summary
            print(result)
            return  result
        return result
    return None

@app.route('/LexRank', methods=['POST'])
def post2():
    print("a")
    if request.method =="POST":
        content = request.get_json()
        result = {}
        result['Summary'] = ''
        if content['text'] is not None:
            if content['percent_output'] is not None:
                per = content['percent_output']
            else:
                per = 0.1
            summary =  lexrank_extract_sum(content['text'], short_count_sentences(content['text'], per))
            result['Summary'] = summary
            print(result)
            return  result
        return result
    return None

@app.route('/MultiLexRank', methods=['POST', 'GET'])
def post5():
    if request.method =="POST":
        content = request.get_json()
        print(content)
        result = {}
        result['result'] = ''
        if content['list_doc'] is not None:
            texts = prep(content['list_doc'])
            print(texts)
            extracted_sen =lexrank_extract_sum(texts, count_sentences(texts))
            summary = extracted_sen
            summary = summary.replace('\"', '"')
            summary = summary.replace("\'", "'")
            summary = summary.replace("\"", '"')
            summary = summary.replace("\\n", '')
            summary = summary.replace("\\", '')
            summary = summary.replace("||||", '')
            summary = summary.replace("  ", ' ')

            result['result'] = summary
            print(result)
            return  result
        return result
    return None

@app.route('/LSA', methods=['POST'])
def post3():
    if request.method =="POST":
        content = request.get_json()
        result = {}
        result['Summary'] = ''
        if content['text'] is not None:
            if content['percent_output'] is not None:
                per = content['percent_output']
            else:
                per = 0.1
            summary =lsa_extract_sum(content['text'], short_count_sentences(content['text'], per))
            print(summary)
            result['Summary'] = summary
            print(result)
            return  result
        return result
    return None

@app.route('/MultiLSA', methods=['POST', 'GET'])
def post6():
    if request.method =="POST":
        content = request.get_json()
        print(content)
        result = {}
        result['result'] = ''
        if content['list_doc'] is not None:
            texts = prep(content['list_doc'])
            print(texts)
            
            extracted_sen =lsa_extract_sum(texts, count_sentences(texts))
            summary = extracted_sen
            summary = summary.replace('\"', '"')
            summary = summary.replace("\'", "'")
            summary = summary.replace("\"", '"')
            summary = summary.replace("\\n", '')
            summary = summary.replace("\\", '')
            summary = summary.replace("||||", '')
            summary = summary.replace("  ", ' ')

            result['result'] = summary
            print(result)
            return  result
        return result
    return None

global is_status
is_status = True

@app.route('/change_status', methods=['POST'])
def post7():
    if request.method =="POST":
        content = request.get_json()
        response_change_status ={}
        response_change_status['result'] = False
        global is_status
        try:
            if content['status'] == True and is_status == False:
                # khởi tạo mô hình
                is_status = True
            elif content['status'] == False and is_status == True:
                # xóa mô hình
                is_status = False
            else:
                print('ok')
            response_change_status['result'] = True
        except:
            response_change_status['result'] = False
    return response_change_status

@app.route('/get_status')
def gett():
    global is_status
    response_status ={}
    response_status['status'] = is_status
    return response_status


app.run(host='0.0.0.0', port=7300,threaded=True)



