import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
import itertools
# Step Two: Load Data
with open ('test.txt', 'r') as f:
    sentence = f.read()

from nltk import pos_tag, sent_tokenize, word_tokenize, ne_chunk

TAG = ['GPE', 'PERSON']

tokenized_doc  = word_tokenize(sentence)
tagged_sentences = nltk.pos_tag(tokenized_doc )
NE= nltk.ne_chunk(tagged_sentences )
# NE.draw()
named_entities = []
for tagged_tree in NE:
    # print(tagged_tree)
    if hasattr(tagged_tree, 'label'):
        entity_name = ' '.join(c[0] for c in tagged_tree.leaves()) #
        entity_type = tagged_tree.label() # get NE category
        if(entity_type in TAG):
            named_entities.append((entity_name, entity_type))

named_entities.sort()

named_entities = list(k for k,_ in itertools.groupby(named_entities))
for en in named_entities:
    print(en)

def get_entity(text):
    tokenized_doc  = word_tokenize(sentence)
    tagged_sentences = nltk.pos_tag(tokenized_doc )
    NE= nltk.ne_chunk(tagged_sentences )
    # NE.draw()
    named_entities = []
    for tagged_tree in NE:
        # print(tagged_tree)
        if hasattr(tagged_tree, 'label'):
            entity_name = ' '.join(c[0] for c in tagged_tree.leaves()) #
            entity_type = tagged_tree.label() # get NE category
            if(entity_type in TAG):
                named_entities.append((entity_name, entity_type))

    named_entities.sort()

    named_entities = list(k for k,_ in itertools.groupby(named_entities))
    return named_entities