from transformers import (
    AutoTokenizer,
    LEDForConditionalGeneration,
)
from datasets import load_dataset, load_metric
import torch
torch_device = torch.device("cuda:0")
dataset=load_dataset('multi_news')
PRIMER_path='allenai/PRIMERA-multinews'
TOKENIZER = AutoTokenizer.from_pretrained(PRIMER_path)
MODEL = LEDForConditionalGeneration.from_pretrained(PRIMER_path).to(torch_device)
# MODEL.gradient_checkpointing_enable()
PAD_TOKEN_ID = TOKENIZER.pad_token_id
DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")

def process_document(documents):
    input_ids_all=[]
    for data in documents:
        all_docs = data.split("|||||")
        for i, doc in enumerate(all_docs):
            doc = doc.replace("\n", " ")
            doc = " ".join(doc.split())
            all_docs[i] = doc
        #open text file
        # text_file = open("/home/dovd/Documents/TextSum/primera/raw.txt", "w")
        
        # #write string to file
        # n = text_file.write('\n'.join(all_docs))
        
        # #close file
        # text_file.close()
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
    return input_ids


def batch_process(batch):
    input_ids=process_document(batch['document'])
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
        max_length=4096,
        num_beams=5,
    )
    generated_str = TOKENIZER.batch_decode(
            generated_ids.tolist(), skip_special_tokens=True
        )
    result={}
    result['generated_summaries'] = generated_str
    # output_sentences =  generated_str[0].split('. ')
    # text_file = open("/home/dovd/Documents/TextSum/primera/predict.txt", "w")
        
    # #write string to file
    # n = text_file.write('.\n'.join(output_sentences))
    
    # #close file
    # text_file.close()
    result['gt_summaries']=batch['summary']
    return result 

import random
data_idx = random.choices(range(len(dataset['test'])),k=5622)
# data_idx = [983]
dataset_small = dataset['test'].select(data_idx)
result_small = dataset_small.map(batch_process, batched=True, batch_size=1)

rouge = load_metric("rouge")

score=rouge.compute(predictions=result_small["generated_summaries"], references=result_small["gt_summaries"])
print(score['rouge1'].mid)
print(score['rouge2'].mid)
print(score['rougeL'].mid)