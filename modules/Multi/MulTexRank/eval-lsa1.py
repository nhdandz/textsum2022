# danh gia text rank, lexrank, lsa voi bo du lieu multi-news
from rouge_score import rouge_scorer
import re
from tqdm import tqdm
import json
import numpy as np
import time

import datasets
from datasets import load_dataset
dataset = load_dataset('multi_news', '3.0.0',split = 'test')

rouge_cal = rouge_scorer.RougeScorer(['rouge1','rouge2', 'rougeLsum'], use_stemmer=True)

count = 0
bath_size = 16
from counter import count_sentences
# extracted_len_list = []
# original_len_list = []
num_extracted_sentences_list = []
extraction_time_list = []
scores = []



from algtm import *
print("Loadmodel: done")
count = 0

for i in range (1, dataset.shape[0]):
    print(i)
    artical = dataset["document"][i]
    highlight = dataset["summary"][i]
    highlight = ' '.join([line.strip() for line in highlight.strip().splitlines()])
    #print('artical: '+artical)
    #print('highlight: '+ highlight)
    tic = time.time()
    #print(tic)
    x = count_sentences(artical)
    print(x)
    extracted_sen = luhn_text_sum(artical, x)
    # batch = tokenizer(artical, truncation=True, padding="longest", return_tensors="pt").to(device)
    # translated = model.generate(**batch)
    # extracted_sen = tokenizer.decode(translated[0])
    #print('out: '+extracted_sen)
    tac = time.time()
    extraction_time_list.append(tac - tic)
    #print(tac)
    score = rouge_cal.score( highlight , extracted_sen )
    if(score["rouge1"].precision >=0.0 ):
        count = count +1
        num_extracted_sentences_list.append( len( extracted_sen ) )
        scores.append( ( score["rouge1"] ,score["rouge2"],score["rougeLsum"]     ) )
        print(score)



rouge1_scores, rouge2_scores, rougel_scores = list(zip(*scores))
res = (       np.asarray( rouge1_scores ).mean(axis = 0).tolist() ,
                np.asarray( rouge2_scores ).mean(axis = 0).tolist() ,
                np.asarray( rougel_scores ).mean(axis = 0).tolist() ,
                )
with open('results/test_results.txt', "a") as f:
    info = " avg. # sentences: %.2f ± %.2f, avg. extraction time: %.2f ± %.2f ms, R-1 (p,r,f1): %.4f, %.4f, %.4f R-2: %.4f, %.4f, %.4f \t R-L: %.4f, %.4f, %.4f\n" % \
            (np.mean( num_extracted_sentences_list ), np.std( num_extracted_sentences_list ) , np.mean( extraction_time_list ) * 1000, np.std( extraction_time_list ) * 1000   , res[0][0], res[0][1], res[0][2], res[1][0], res[1][1], res[1][2], res[2][0], res[2][1], res[2][2],  )

    f.write(info)
print(info)
