import re
from flask_api import status
from flask_cors import CORS
from flask import Flask,request,Response
# import multiprocessing, Queue
from multiprocessing import Process, Manager
from multiprocessing import Pool
import time
import concurrent.futures

from threading import Thread 
import queue
from helper import get_raw_text_by_topic,check_short,get_raw_text,get_number_page
# from preprocess import preprocess_memsum

app = Flask(__name__)
CORS(app)

# def worker(out_queue,doc):
#     result_doc = {}
#     text_input = get_raw_text(doc['encode'],doc['file_type'],doc['page_from'],doc['page_to'])
#     result_doc['text'] = text_input
#     result_doc['documents_id'] = doc['documents_id']    
#     out_queue.put(result_doc)
def worker(doc):
    try:
        result_doc = {}
        text_input = get_raw_text(doc['encode'],doc['file_type'],doc['page_from'],doc['page_to'])
        result_doc['text'] = text_input
        result_doc['documents_id'] = doc['documents_id']
    except:
        result_doc['text'] = ""
        result_doc['documents_id'] = doc['documents_id']
    return result_doc



@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/get_number_page', methods=['POST'])
def post():
    content = request.get_json() 
    number_page = get_number_page(content['encode'],content['file_type'])
    result = {}
    result['number_page'] = number_page
    return result

@app.route('/get_content', methods=['POST'])
def post1():
    result = {}
    result['result'] = []
    result['message'] = ''
    try:
        content = request.get_json() 
        data =  content['data']
        print('len data :' + str(len(data)))
    except:
        result['message'] = 'sai định dạng'
    try:
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            start_time = time.perf_counter()
            result_doc = list(executor.map(worker, data))
            finish_time = time.perf_counter()
        end = time.time()
        result['result'] = result_doc
        print(f"Program finished in {finish_time-start_time} seconds")
        print(f"Program finished in {end-start} seconds")
    except:
        result['message'] = 'tóm tắt lỗi'
    return result

@app.route('/check_short', methods=['POST'])
def post2():
    content = request.get_json() 
    is_short = check_short(content['text'])
    result = {}
    result['is_short'] = is_short
    return result

@app.route('/check_short_topic', methods=['POST'])
def post3():
    content = request.get_json() 
    raw_text_topic = get_raw_text_by_topic(content['keywords'],content['text'])
    is_short = check_short(raw_text_topic)
    result = {}
    result['is_short'] = is_short
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9980,threaded=True)