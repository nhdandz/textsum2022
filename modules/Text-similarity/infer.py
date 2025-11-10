# import nltk
# import pandas as pd

# nltk.download('wordnet')
# nltk.download('omw-1.4')
# from nltk.stem import WordNetLemmatizer
# import nltk
# from nltk.corpus import stopwords
# nltk.download('punkt')
# import re
# from isqrt import isqrt
# def cleaning ( text ):
# # Remove new line , new tab
#     text = re . sub (r"\n", ' ', text )
#     text = re . sub (r"\t",' ', text )
#     re.sub(r'http\S+', '', text)
#     # Remove URL    # Remove HTML
#     text = re . sub (r' <.*? > ', '', text )
#     # Remove Email
#     text = re . sub ('\S+@[a-zA -Z ]+\.[a-zA -Z]+ ', '', text )
#     # Remove repeating chars
#     text = re . sub (r"!+", "! ", text )
#     text = re . sub (r" \.+ ", ". ", text )
#     text = re . sub (r" \?+ ", "? ", text )
#     text = re . sub (r" \*+ ", "* ", text )
#     text = re . sub (r"\ >+", "> ", text )
#     text = re . sub (r"\ <+", "< ", text )
#     # Clean shorthands
#     text = re.sub("\\n", "", text)
#     text = re . sub ("\'s"," ", text )
#     text = re . sub ("\'ve"," have ", text )
#     text = re . sub ("\'re", " are ", text )
#     text = re . sub ("\'ll", " will ", text )
#     text = re . sub ("I'm", "I am", text )
#     text = re . sub ("\'d", " would ", text )
#     text = re . sub ("n't", " not ", text )
#     text = re . sub (" can 't", " can not ", text , flags = re . IGNORECASE )
#     text = re . sub ("i\.e\.", "id est ", text , flags = re . IGNORECASE )
#     text = re . sub ("e\.g\.", " for example ", text , flags = re . IGNORECASE )
#     text = re . sub ("e- mail ", " email ", text , flags = re . IGNORECASE )
#     # Remove comma between numbers
#     #text = re . sub (" (? <=[0 -9]) \ ,(?=[0 -9]) '", "", text )
#     # Special characters
#     text = re . sub ("\$"," dollar ", text )
#     text = re . sub ("\&", " and ", text )
#     text = re . sub ("\%", " percent ", text )
#     text = text.replace("\n", "")
#     # Remove non ascii character
#     text_non_ascii = ""
#     for i in text :
#         num = ord (i)
#         if( num >= 0) :
#           if( num <= 121) :
#             text_non_ascii = text_non_ascii +i
#     text = text_non_ascii
#     # Remove smiley faces such as :) , :( , : -) and : -(
#     text = re . sub (r" :\) |:\(|: -\(|: -\) ",' ', text )
#     # Remove 's'
#     text = re . sub (' s ', " ", text )
#     # Remove extra spaces
#     text = re . sub ("[\s]+", " ", text )
#     text = re . sub ("[=]+", " ", text )
#     list2 = nltk.word_tokenize(text)

#     text = ' '.join([wnl.lemmatize(words) for words in list2])
    
#     # Strip text
#     text = text . strip ()
#     return text

# from sklearn.feature_extraction.text import TfidfVectorizer
# vectorizer = TfidfVectorizer(stop_words={'english'})
# from sklearn.cluster import KMeans
# # Create WordNetLemmatizer object
# wnl = WordNetLemmatizer()

# import math
# def text_cluster(texs, num):
#     texs = [cleaning(l) for l in texs]
#     idx = []
#     i = 0
#     for l in texs:
#         idx.append(i)
#         i = i+1
#     X = vectorizer.fit_transform(texs)
#     true_k = round(isqrt(num))
#     if (num <= 2):
#         true_k = num
#     model = KMeans(n_clusters=true_k, init='k-means++', n_init=10, random_state=100)
#     model.fit(X)
#     labels=model.labels_
#     wiki_cl=pd.DataFrame(list(zip(idx,labels)),columns=['idx','cluster'])
#     result = wiki_cl.sort_values(by=['cluster']).values.tolist()
#     temp_list = []
#     result_list = []
#     current_cluster = 0
#     for item in result:
#         if (item[1] == current_cluster):
#             temp_list.append(item[0])
#         else:
#             result_list.append(temp_list)
#             temp_list = [item[0]]
#             current_cluster = item[1]
#     result_list.append(temp_list)
#     return result_list


#######################Tieng Viet ##########################
import re
import nltk
import pandas as pd
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from isqrt import isqrt

# Stopwords tiếng Việt (có thể mở rộng thêm)
VIETNAMESE_STOPWORDS = set([
    "và", "là", "có", "các", "cho", "một", "được", "trong", "khi", "với",
    "vì", "từ", "này", "đó", "nhưng", "đã", "theo", "cũng", "nên", "sẽ",
    "thì", "làm", "để", "rất", "hơn", "nhiều", "như", "lại", "nào", "ai",
    "cái", "gì", "ở", "ra", "đi", "đâu", "sao"
])

def cleaning(text):
    # Làm sạch cơ bản
    text = re.sub(r"\n|\t", " ", text)
    text = re.sub(r"http\S+", "", text)              # bỏ URL
    text = re.sub(r'<.*?>', '', text)                # bỏ HTML tag
    text = re.sub(r'\S+@\S+', '', text)              # bỏ email
    text = re.sub(r'[^\w\sÀ-ỹà-ỹ.,!?;:()"\']+', ' ', text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)

    # Tách từ theo tiếng Việt
    tokens = word_tokenize(text, format="text").split()
    tokens = [word for word in tokens if word.lower() not in VIETNAMESE_STOPWORDS]

    return " ".join(tokens).strip()

# Vectorizer tiếng Việt
vectorizer = TfidfVectorizer()

def text_cluster(texs, num):
    texs = [cleaning(l) for l in texs]
    idx = list(range(len(texs)))

    X = vectorizer.fit_transform(texs)
    true_k = min(num, isqrt(num)) if num > 2 else num

    model = KMeans(n_clusters=true_k, init='k-means++', n_init=10, random_state=100)
    model.fit(X)
    labels = model.labels_

    wiki_cl = pd.DataFrame(list(zip(idx, labels)), columns=['idx', 'cluster'])
    result = wiki_cl.sort_values(by=['cluster']).values.tolist()

    temp_list, result_list = [], []
    current_cluster = result[0][1]

    for item in result:
        if item[1] == current_cluster:
            temp_list.append(item[0])
        else:
            result_list.append(temp_list)
            temp_list = [item[0]]
            current_cluster = item[1]
    result_list.append(temp_list)
    return result_list
