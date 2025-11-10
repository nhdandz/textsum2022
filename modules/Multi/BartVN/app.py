from flask_api import status
from flask_cors import CORS
from flask import Flask,request
import pathlib
import os
from helper import batch_process, post_process_document,split_doc
from transformers import (
    AutoTokenizer,
    LEDConfig,
    LEDForConditionalGeneration,
)

from datasets import load_dataset, load_metric
import torch
app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())

# dataset= load_dataset('multi_news')

TOKENIZER= None
MODEL=None
PAD_TOKEN_ID = None
DOCSEP_TOKEN_ID  = None
# is_status = False
is_status = True
torch_device = torch.device("cuda:0")
TOKENIZER = AutoTokenizer.from_pretrained('allenai/PRIMERA')
config=LEDConfig.from_pretrained('allenai/PRIMERA')
MODEL = LEDForConditionalGeneration.from_pretrained('allenai/PRIMERA').to(torch_device)

PAD_TOKEN_ID = TOKENIZER.pad_token_id
DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")

pid= None


def run(status):
    global MODEL
    global TOKENIZER
    global PAD_TOKEN_ID
    global DOCSEP_TOKEN_ID
    global is_status
    if status == False:
        os.system(f'python kill.py {pid}')
        # print("*aadhfalkdflaskjdf")
        return

    if status ==True:
        if MODEL==None:
            is_status = True
            TOKENIZER = AutoTokenizer.from_pretrained('allenai/PRIMERA')
            config=LEDConfig.from_pretrained('allenai/PRIMERA')
            MODEL = LEDForConditionalGeneration.from_pretrained('allenai/PRIMERA')

            PAD_TOKEN_ID = TOKENIZER.pad_token_id
            DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")
            print('Done')
@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/primera', methods=['POST'])
def post():
    if request.method =="POST":
        if is_status == True:
            global MODEL
            global TOKENIZER
            global PAD_TOKEN_ID
            global DOCSEP_TOKEN_ID
            content = request.get_json() 
            process_data =  post_process_document(content['list_doc'])
            data =  split_doc(process_data[0],4096)
            result =  batch_process(process_data,MODEL,TOKENIZER,DOCSEP_TOKEN_ID,PAD_TOKEN_ID)
        else:
            print('2')
            TOKENIZER = AutoTokenizer.from_pretrained('allenai/PRIMERA')
            config=LEDConfig.from_pretrained('allenai/PRIMERA')
            MODEL = LEDForConditionalGeneration.from_pretrained('allenai/PRIMERA')

            PAD_TOKEN_ID = TOKENIZER.pad_token_id
            DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")
            content = request.get_json() 
            process_data =  post_process_document(content['raw_text'])
            data =  split_doc(process_data[0],4096)
            result =  batch_process(process_data,MODEL,TOKENIZER,DOCSEP_TOKEN_ID,PAD_TOKEN_ID)
        print(result)
        torch.cuda.empty_cache()
    return result,200

@app.route('/change_status', methods=['POST'])
def post_change():
    content = request.get_json()  
    status = content["status"]
    run(status)
    return {"result":True} 

pid = os.getpid()
app.run(host='0.0.0.0', port=4100,threaded=True)