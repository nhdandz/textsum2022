import torch
from nltk.tokenize import sent_tokenize, word_tokenize
import unicodedata
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re


alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def batch_process(data,MODEL,TOKENIZER,DOCSEP_TOKEN_ID,PAD_TOKEN_ID):
    input_ids,all_docs=process_document(data,TOKENIZER,DOCSEP_TOKEN_ID,PAD_TOKEN_ID)
    input_ids = input_ids.cuda()
    # get the input ids and attention masks together
    global_attention_mask = torch.zeros_like(input_ids).to(input_ids.device)
    # put global attention on <s> token

    global_attention_mask[:, 0] = 1
    global_attention_mask[input_ids == DOCSEP_TOKEN_ID] = 1
    generated_ids = MODEL.generate(
        input_ids=input_ids,
        global_attention_mask=global_attention_mask,
        use_cache=True,
        max_length=2048,
        num_beams=5,
    )
    generated_str = TOKENIZER.batch_decode(
            generated_ids.tolist(), skip_special_tokens=True
        )
    return generated_str[0][1:]
def post_process_document(list_doc):
    doc_final = ""
    # for doc in list_doc:
    #     doc_final= doc_final+' ||||| '+doc
    doc_final = ' ||||| '.join(list_doc)
    return [doc_final]
def process_document(datas,TOKENIZER,DOCSEP_TOKEN_ID,PAD_TOKEN_ID):
    input_ids_all=[]
    for data in datas:
        all_docs = data.split("|||||")
        for i, doc in enumerate(all_docs):
            doc = doc.replace("\n", " ")
            doc = " ".join(doc.split())
            all_docs[i] = doc

        #### concat with global attention on doc-sep
        input_ids = []
        for doc in all_docs:
            input_ids.extend(
                TOKENIZER.encode(
                    doc,
                    truncation=True,
                    max_length=4096 // len(all_docs),
                )[1:-1]
            )
            input_ids.append(DOCSEP_TOKEN_ID)
        input_ids = (
            [TOKENIZER.bos_token_id]
            + input_ids
            + [TOKENIZER.eos_token_id]
        )
        input_ids_all.append(torch.tensor(input_ids))
    input_ids = torch.nn.utils.rnn.pad_sequence(
        input_ids_all, batch_first=True, padding_value=PAD_TOKEN_ID
    )
    return input_ids,all_docs
def split_doc(text, max_length):
    """
    doc: document >=4096 word
    max_length: length maximun to input summary
    output: split doc to mul small doc
    """

    word_tokens_split = word_tokenize(text)
    if len(word_tokens_split)<=max_length:
        return [text]
    sentence_tokens = sent_tokenize(text)

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


def summary_func(content_list,MODEL,TOKENIZER,DOCSEP_TOKEN_ID):
    process_data =  post_process_document(content_list)
    list_data =  split_doc(process_data[0],4096)
    list_result = []
    for data in list_data:
        result =  batch_process([data],MODEL,TOKENIZER,DOCSEP_TOKEN_ID,DOCSEP_TOKEN_ID)
        list_result.append(result)
    text_summary = "\n\t\t"+ '\n\t\t'.join(list_result)
    return text_summary
      

