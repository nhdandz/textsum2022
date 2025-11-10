# importing the requests library
import requests
from threading import Thread 
import time
# api-endpoint
URL = "http://${HOST_IP}:9980/get_content"
# URL = "http://${HOST_IP}:9980/get_number_page"
# URL = "http://${HOST_IP}:9980/check_short"
# URL = "http://${HOST_IP}:9980/check_short_topic"
# location given here
location = '''Anxiety affects quality of life in those living with Parkinson's disease (PD) more so than overall cognitive status, motor deficits, apathy, and depression [1–3]. Although anxiety and depression are often related and coexist in PD patients [4], recent research suggests that anxiety rather than depression is the most prominent and prevalent mood disorder in PD [5, 6]. Yet, our current understanding of anxiety and its impact on cognition in PD, as well as its neural basis and best treatment practices, remains meager and lags far behind that of depression [7].
Overall, neuropsychiatric symptoms in PD have been shown to be negatively associated with cognitive performance. For example, higher depression scores have been correlated with lower scores on the Mini-Mental State Exam (MMSE) [8, 9] as well as tests of memory and executive functions (e.g., attention) [10–14]. Likewise, apathy and anhedonia in PD patients have been associated with executive dysfunction [10, 15–23]. However, few studies have specifically investigated the relationship between anxiety and cognition in PD.
One study showed a strong negative relationship "between" anxiety (both state and trait) and overall cognitive performance (measured by the total of the repeatable battery for the assessment of neuropsychological status index) within a sample of 27 PD patients [24]. Furthermore, trait anxiety was negatively associated with each of the cognitive domains assessed by the RBANS (i.e., immediate memory, visuospatial construction, language, attention, and delayed memory). Two further studies have examined whether anxiety differentially affects cognition in patients with left-sided dominant PD (LPD) versus right-sided dominant PD (RPD); however, their findings were inconsistent. The first study found that working memory performance was worse in LPD patients with anxiety compared to RPD patients with anxiety [25], whereas the second study reported that, in LPD, apathy but not anxiety was associated with performance on nonverbally mediated executive functions and visuospatial tasks (e.g., TMT-B, WMS-III spatial span), while in RPD, anxiety but not apathy significantly correlated with performance on verbally mediated tasks (e.g., clock reading test and Boston naming test) [15]. Furthermore, anxiety was significantly correlated with neuropsychological measures of attention and executive and visuospatial functions [15]. Taken together, it is evident that there are limited and inconsistent findings describing the relationship between anxiety and cognition in PD and more specifically how anxiety might influence particular domains of cognition such as attention and memory and executive functioning. It is also striking that, to date, no study has examined the influence of anxiety on cognition in PD by directly comparing groups of PD patients with and without anxiety while excluding depression. This was the primary objective of the current study.
Given that research on healthy young adults suggests that anxiety reduces processing capacity and impairs processing efficiency, especially in the central executive and attentional systems of working memory [26, 27], we hypothesized that PD patients with anxiety would show impairments in attentional set-shifting and working memory compared to PD patients without anxiety. Furthermore, since previous work, albeit limited, has focused on the influence of symptom laterality on anxiety and cognition, we also explored this relationship.
   '''
# f = open("/home/user01/Documents/API/Single_API/encoded-20220930143020.txt", "r")
# encode =  f.read()
f = open("./encoded-20220930142500.txt", "r")
encode =  f.read()
  
# defining a params dict for the parameters to be sent to the API

PARAMS = {'data':[
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }, 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }, 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                , 
                {
                "documents_id":'sssss', 
                "encode":encode, 
                'file_type' :1, 
                'page_from':0, 
                'page_to':9999
                }
                
                ]
            }

# sending get request and saving the response as response object
# PARAMS = {"encode":encode,
#             'file_type' :1, 
#             "keywords":[["Anxiety"],[]]
#             }
start = time.time()
def run():
    r =  requests.post(url = URL, json=PARAMS)
    # print(r.json())
    print('done')
# run()

k=0
# for j in range(10):
for i in range(100):
    threads = []
    thread1 = Thread(target=run, args=())
    threads.append(thread1)
for t in threads:
    t.start()
count = 0
for t in threads:
    count+=1
    t.join()
    print(count)
end = time.time()
print(f"Program finished in {end-start} seconds")
# import multiprocessing
# import math

# def worker(argument):
#     for i in range(200000):
#         print(math.sqrt(i))
#     return

# for i in range(3):
#     t = multiprocessing.Process(target=worker, args=[i])
#     t.start()