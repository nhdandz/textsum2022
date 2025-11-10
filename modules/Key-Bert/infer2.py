# su dung spacy
import time
from tkinter import NONE
import spacy
from keybert import KeyBERT
spacy.prefer_gpu()
import en_core_web_sm
nlp = en_core_web_sm.load()

kw_model = KeyBERT(model=nlp)
# kw_model2 = 

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text

with open ('test.txt', 'r') as f:
    text = f.read()
seed_kws = ['putin']
tic = time.time()
keywords = kw_model.extract_keywords(text, top_n=5, keyphrase_ngram_range=(1, 2), stop_words='english')
print(time.time() - tic)
print(keywords)