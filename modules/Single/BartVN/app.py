
from flask_api import status
from flask_cors import CORS
from flask import Flask,request
import pathlib
from transformers import  pipeline
import nvidia_smi

nvidia_smi.nvmlInit()

handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
# card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate

info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)

print("Total memory:", info.total)
print("Free memory:", info.free)
print("Used memory:", info.used)
# summarizer = pipeline('summarization', model='bart-large-cnn')


app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())
import torch
import transformers
from transformers import BartTokenizer, BartForConditionalGeneration
device = "cuda:0" #if torch.cuda.is_available() else "cpu"
torch_device = torch.device("cuda:0")
# tokenizer_large = BartTokenizer.from_pretrained('bart-large-cnn', local_files_only=True)
# bart_large_model = BartForConditionalGeneration.from_pretrained('bart-large-cnn')
# bart_large_model = bart_large_model.to(device)
#
# ##
# bart_d_66_tokenizer = BartTokenizer.from_pretrained("distilbart-cnn-6-6", local_files_only=True)
# bart_d_66_model = BartForConditionalGeneration.from_pretrained("distilbart-cnn-6-6")
#
# bart_d_66_model = bart_d_66_model.to(device)

main_tokenizer= None
main_model=None
main_pipe= None
pid= None


import time
tic = time.time()
# bart_d_126_tokenizer = BartTokenizer.from_pretrained("distilbart-cnn-12-6", local_files_only=True)
# bart_d_126_model = BartForConditionalGeneration.from_pretrained("distilbart-cnn-12-6")
device = "cuda:0" #if torch.cuda.is_available() else "cpu"
import os

tac = time.time()
print(tac - tic)

def run(status):
    global main_model
    global main_tokenizer
    global main_pipe

    if status == False:
        os.system(f'python kill.py {pid}')
        return

    if status ==True:
        if main_model==None:
            main_tokenizer=BartTokenizer.from_pretrained("distilbart-cnn-12-6", local_files_only=True)
            main_model=BartForConditionalGeneration.from_pretrained("distilbart-cnn-12-6")
            main_model = main_model.to(device)

run(True)

handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
# card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate

info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
print("Total memory:", info.total)
print("Free memory:", info.free)
print("Used memory:", info.used)
##
text = """
Python is an interpreted high-level general-purpose programming language. Its design philosophy emphasizes code readability with its use of significant indentation. Its language constructs as well as its object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.[30]

Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly, procedural), object-oriented and functional programming. It is often described as a "batteries included" language due to its comprehensive standard library.[31]

Guido van Rossum began working on Python in the late 1980s, as a successor to the ABC programming language, and first released it in 1991 as Python 0.9.0.[32] Python 2.0 was released in 2000 and introduced new features, such as list comprehensions and a garbage collection system using reference counting. Python 3.0 was released in 2008 and was a major revision of the language that is not completely backward-compatible. Python 2 was discontinued with version 2.7.18 in 2020.[33]

Python consistently ranks as one of the most popular programming languages.[34][35][36][37]"""


@app.route('/')
def GetStatusService():
    return 'ok'

# @app.route('/BARTLarge', methods=['POST'])
# def post():
#     if request.method =="POST":
#         content = request.get_json()
#         result = {}
#         result['Model'] = 'Bart large CNN'
#         result['Summary'] = ''
#         if content['text'] is not None:
#             text = content['text'] = ' '.join(line.strip() for line in content['text'].strip().splitlines())
#             text.replace('\n', ' ')
#             article_input_ids = tokenizer_large.batch_encode_plus([text], return_tensors='pt', max_length=1024, truncation=True)['input_ids'].to(device)
#             summary_ids = bart_large_model.generate(article_input_ids,
#                                                     num_beams=4,
#                                              length_penalty=2.0,
#                                              max_length=140,
#                                              min_length=20,
#                                              no_repeat_ngram_size=3).to(torch_device)
#             summary_txt = tokenizer_large.decode(summary_ids.squeeze(), skip_special_tokens=True)
#             result['Summary'] = summary_txt
#             print(result)
#             return  result
#         return result
#     return None
global is_status
is_status = True

@app.route('/BARTD126', methods=['POST'])
def post2():
    if request.method =="POST":
        content = request.get_json()
        result = {}

        result['Summary'] = ''
        if content['text'] is not None:
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
            info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
            before = info.free
            if(content['text'] ==""):
                return result
            text = content['text'] = ' '.join(line.strip() for line in content['text'].strip().splitlines())
            text.replace('\n', ' ')
            inputs = main_tokenizer(text, max_length=1024,truncation=True, return_tensors="pt").to(device)
            # Generate Summary
            summary_ids = main_model.generate(inputs["input_ids"], min_length=0, max_length=160)
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
            info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
            after = info.free
            print("Multi: "+ str(after-before))   
            summary_txt = main_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
            #
            result['Summary'] = summary_txt
            print(result)
            torch.cuda.empty_cache()
            return  result
        return result
    return None

@app.route('/change_status', methods=['POST'])
def post3():
    if request.method =="POST":
        content = request.get_json()
        status = content["status"]
        run(status)
        return {"result":True}

@app.route('/get_status')
def get():
    global is_status
    response_status ={}
    response_status['status'] = is_status
    return response_status
# @app.route('/BARTD66', methods=['POST'])
# def post3():
#     if request.method =="POST":
#         content = request.get_json()
#         result = {}
#         result['Model'] = 'MemSum'
#         result['Summary'] = ''
#         if content['text'] is not None:
#             # P-P
#             text = content['text'] = ' '.join(line.strip() for line in content['text'].strip().splitlines())
#             text.replace('\n', ' ')
#             print(text)
#             inputs = bart_d_66_tokenizer([text], max_length=1024,truncation=True, return_tensors="pt").to(device)
#             # Generate Summary
#             summary_ids = bart_d_66_model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=60)
#             summary_txt = bart_d_66_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
#             #
#             result['Summary'] = summary_txt
#             print(result)
#             return  result
#         return result
#     return None

app.run(host='0.0.0.0', port=6400,threaded=True)
