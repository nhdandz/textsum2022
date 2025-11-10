from flask_api import status
from flask_cors import CORS
from flask import Flask,request
import pathlib
from flask import make_response
from json import dumps

from werkzeug.utils import secure_filename

from infer import get_entity
from infercopy import getNER2, getNER
app = Flask(__name__)
CORS(app)
current_path = str(pathlib.Path(__file__).parent.absolute())
from tkinter import NONE
import time

# from nltk import get_entity
#from spacy import getNER

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text


@app.route('/')
def GetStatusService():
    return 'ok'

@app.route('/NER2', methods=['POST'])
def post2():
    if request.method =="POST":
        content = request.get_json()
        result = {}
        if content['text'] is not None:
            text = content['text']
        else: 
            return None        
        print(text)
        result = {}
        ents = getNER(text)
        print(dumps(ents))
        return make_response(dumps(ents))

    return None

@app.route('/NER1', methods=['POST'])
def post3():
    if request.method =="POST":
        content = request.get_json()
        result = {}
        if content['text'] is not None:
            text = content['text']
        else: 
            return None        
        print(text)
        result = {}
        ents = get_entity(text)
        print(dumps(ents))
        return make_response(dumps(ents))
    return None
app.run(host='0.0.0.0', port=2300,threaded=True)
