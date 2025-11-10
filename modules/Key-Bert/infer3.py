# su dung spacy
import time
from tkinter import NONE

from keybert import KeyBERT
import tensorflow_hub
embedding_model = tensorflow_hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
kw_model = KeyBERT(model=embedding_model)

def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text

with open ('test.txt', 'r') as f:
    text = f.read()
seed_kws = ['putin']
tic = time.time()
keywords = kw_model.extract_keywords(text, top_n=5, stop_words='english')#keyphrase_ngram_range=(1, 2), 
print(time.time() - tic)
print(keywords)