from flask_api import status
from flask_cors import CORS
from flask import Flask,request
import pathlib
import torch
from flask import make_response
from json import dumps

from werkzeug.utils import secure_filename
import itertools

app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())
from tkinter import NONE
import time
from keybert import KeyBERT
print('done')
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text

torch_device = torch.device("cuda:0")

@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/KeyBert', methods=['POST'])
def post2():
    if request.method =="POST":
        text = request.form['text']
        print(text)
        result = {}
        # result['Model'] = 'MemSum'
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
        #keywords = kw_model.extract_keywords(text,top_n=5,nr_candidates=5,use_maxsum=True,  stop_words='english')
        keywords = [key[0] for key in keywords]
        return make_response(dumps(keywords))
    return None

@app.route('/KeyBertArr', methods=['POST'])
def post3():
    if request.method =="POST":
        all_keywords = []
        if(request.data):
            docs = request.get_json()['text']
            for doc in docs:
                text = doc
                print(text)
                result = {}
                # result['Model'] = 'MemSum'
                keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
                #keywords = kw_model.extract_keywords(text, top_n=5, keyphrase_ngram_range=(1, 2), stop_words='english', use_mmr=True)#, diversity=0.8)
                keywords = [key[0] for key in keywords]
                all_keywords.extend(keywords)
        all_keywords.sort()
        all_keywords = list(k for k,_ in itertools.groupby(all_keywords))
        print(all_keywords)
        return make_response(dumps(all_keywords))
    return None


app.run(host='0.0.0.0', port=8200,threaded=True)
