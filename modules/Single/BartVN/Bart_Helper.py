from nltk.tokenize import sent_tokenize, word_tokenize
import unicodedata
from nltk.tokenize.treebank import TreebankWordDetokenizer

import re 
import nltk
from nltk import tokenize

nltk.download('words')
words = set(nltk.corpus.words.words())

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def replace_unneeded_items(string):
    replace_list = {
        # chuẩn hóa dấu câu
        # loại bỏ các dấu
        '\n':' ','"':'','‘':'','’':'','*':'', '(':'', ')':'','…':''
    }
    for k, v in replace_list.items():
        string = string.replace(k, v)

    string = re.sub("([.]{2,})","", string)
    string = re.sub(" +"," ", string)
    string = string.strip()
    return string

def remove_duplicate(x): 
  return list(dict.fromkeys(x))


def preprocess_pegasus(doccument):
    doccument = doccument.lower()
    doccument = " ".join(w for w in nltk.wordpunct_tokenize(doccument) \
         if w.lower() in words or not w.isalpha())
    doccument = replace_unneeded_items(doccument)
    return doccument


def post_process_output_bigbird(output_text):
    output_text = output_text.replace("<s>", "").replace("</s>","").replace("<n>", "").replace("\n", "")
    output_text = output_text.split(". ")
    output_text = '. '.join(text.strip() for text in output_text)
    output_text = output_text.replace(".aims", f".\nAims")
    output_text = output_text.replace(".results", f".\nResults")
    output_text = output_text.replace(".materials and methods", f".\nMaterials and methods")
    return output_text.rstrip()

def split_doc(text, max_length):
    """
    doc: document >=4096 word
    max_length: length maximun to input summary
    output: split doc to mul small doc
    """

    word_tokens_split = word_tokenize(text)
    if len(word_tokens_split)<=max_length:
        return [text]
    sentence_tokens = remove_duplicate( sent_tokenize(text))

    length_text = len(word_tokens_split)
    doc_split_num = length_text // max_length + 1

    word_in_sub_doc = length_text // doc_split_num
    count = 0
    text  = ""
    result = []
    count_doc = 0
    for sentence in sentence_tokens:
        count += len(word_tokenize(sentence))
        if count > word_in_sub_doc:
            count = 0
            count_doc +=1
            result.append(text)
            text = ""
        text += " ".join(sentence.split()) +" "
    # append last doc
    if count_doc < doc_split_num:
        result.append(text)
    return result


def split_shot_doc(text):
    word_tokens_split = word_tokenize(text)
    if len(word_tokens_split)<=400:
        return [text]
    sentence_tokens = remove_duplicate( sent_tokenize(text))

    length_text = len(word_tokens_split)
    doc_split_num = 2

    word_in_sub_doc = length_text // doc_split_num
    count = 0
    text  = ""
    result = []
    count_doc = 0
    for sentence in sentence_tokens:
        count += len(word_tokenize(sentence))
        if count > word_in_sub_doc:
            count = 0
            count_doc +=1
            result.append(text)
            text = ""
        text += " ".join(sentence.split()) +" "
    # append last doc
    if count_doc < doc_split_num:
        result.append(text)
    return result    