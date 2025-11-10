from flask_api import status
from flask_cors import CORS
from flask import Flask,request
import pathlib
# import torch
from flask import make_response
from json import dumps

from werkzeug.utils import secure_filename
import itertools
from spacy2 import *
from keybert import KeyBERT
print('done')
kw_model = KeyBERT(model='all-MiniLM-L6-v2')
app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())
from tkinter import NONE
import time
# from keybert import KeyBERT
# print('done')
# kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text

# torch_device = torch.device("cuda:0")
import yake
kw_extractor = yake.KeywordExtractor()
def get_keys(text):
    text = text.lower()
    language = "en"
    max_ngram_size = 2
    deduplication_threshold = 0.2
    numOfKeywords = 5
    custom_kw_extractor1 = yake.KeywordExtractor(lan=language, n=1, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    custom_kw_extractor2 = yake.KeywordExtractor(lan=language, n=2, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)

    ks1 =custom_kw_extractor1.extract_keywords(text)
    ks2 =custom_kw_extractor2.extract_keywords(text)
    # for k in ks1:
    #     for k1 in ks2:
    #         if(k[0] not in k1[0]):
    #             ks1.append(k)
        
    ks1 = sorted(ks2, key=lambda x: x[1])
    result = []
    for k in ks1:
        result.append(k[0])
    re2 =[]
    for k in result:
        for k1 in result:
            if (k ==k1 or (k != k1 and k not in k1)):
                re2.append(k)
    re2 = list(k for k,_ in itertools.groupby(re2))
    return re2
@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/KeyBert', methods=['POST'])
def post2():
    if request.method =="POST":
        text = request.form['text']
        print(text)
        keywords = get_keys(text)
        # result['Model'] = 'MemSum'
        # keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
        #keywords = kw_model.extract_keywords(text,top_n=5,nr_candidates=5,use_maxsum=True,  stop_words='english')
        #keywords = [key[0] for key in keywords]
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
                # result['Model'] = 'MemSum'
                # keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
                # #keywords = kw_model.extract_keywords(text, top_n=5, keyphrase_ngram_range=(1, 2), stop_words='english', use_mmr=True)#, diversity=0.8)
                # keywords = [key[0] for key in keywords]
                keywords = get_keys(text)
                all_keywords.extend(keywords)
        all_keywords.sort()
        all_keywords = list(k for k,_ in itertools.groupby(all_keywords))
        print(all_keywords)
        return make_response(dumps(all_keywords))
    return None
@app.route('/KeyBert2', methods=['POST'])
def post4():
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

@app.route('/KeyBertArr2', methods=['POST'])
def post5():
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
@app.route('/KeyBert3', methods=['POST'])
def post6():
    if request.method =="POST":
        text = request.form['text']
        print(text)
        keywords = getKeyWords_spacy(text)
        return make_response(dumps(keywords))
    return None

@app.route('/KeyBertArr3', methods=['POST'])
def post7():
    if request.method =="POST":
        all_keywords = []
        if(request.data):
            docs = request.get_json()['text']
            for doc in docs:
                text = doc
                print(text)
                keywords = getKeyWords_spacy(text)
                all_keywords.extend(keywords)
        all_keywords.sort()
        all_keywords = list(k for k,_ in itertools.groupby(all_keywords))
        print(all_keywords)
        return make_response(dumps(all_keywords))
    return None

app.run(host='0.0.0.0', port=8200,threaded=True)
