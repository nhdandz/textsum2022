from tkinter import NONE
import time
from keybert import KeyBERT
print('done')
kw_model = KeyBERT()#model='all-MiniLM-L6-v2')
# kw_model2 = 

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text

with open ('test.txt', 'r') as f:
    text = f.read()
seed_kws = ['putin']
tic = time.time()
print('done')
keywords = kw_model.extract_keywords(text, stop_words='english',keyphrase_ngram_range=(1, 2),top_n=15)#,use_maxsum=True)#,keyphrase_ngram_range=(1, 2), stop_words='english',  diversity=0.1)#, diversity=0.7)#, ,top_n=15, ,)#, 
tac  = time.time()
print(tac - tic)
print(keywords)