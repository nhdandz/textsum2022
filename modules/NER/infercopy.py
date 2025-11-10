import spacy
def preprocess(text):
    text = " ".join(tex for tex in text.split())
    return text
import itertools
nlp = spacy.load('en_core_web_sm')
# ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 
# 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']
TAG = ['GPE', 'ORG', 'PERSON', 'EVENT', 'EVENT', 'FAC','LANGUAGE', 'LAW', 'LOC',   'NORP',  'ORG', 'PERCENT',  'PRODUCT', 'QUANTITY',  'WORK_OF_ART']
# with open('test.txt', 'r')as f:
#     text = f.read()
# text = preprocess(text)
# doc = nlp(text)
# entities = []
# for en in doc.ents:
#     if(en.label_ in TAG):
#         entities.append([en.text, en.label_])
# entities.sort()
# entities = list(k for k,_ in itertools.groupby(entities))
# for en in entities:
#     print(en)

def getNER(text):
    doc = nlp(text)
    entities = []
    for en in doc.ents:
        if(en.label_ in TAG):
            entities.append([ en.label_, en.text])
    entities.sort()
    entities = list(k for k,_ in itertools.groupby(entities))
    return entities

def getNER2(text):
    doc = nlp(text)
    entities = []
    for en in doc.ents:
        if(en.label_ in TAG):
            entities.append(en.text)
    entities.sort()
    entities = list(k for k,_ in itertools.groupby(entities))
    return entities