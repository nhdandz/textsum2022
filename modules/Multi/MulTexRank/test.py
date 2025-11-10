from algtm import *
from counter import *
from prep import *

text = ""
with open("f1.txt", "r") as f:
    text  = f.read()
print(type(text))

# # texs = text.split("||||")[:-1]
ts = lsa_extract_sum2(text, short_count_sentences(text, 0.1))
ts = sortByDocToStr(text, ts)
print(ts)
