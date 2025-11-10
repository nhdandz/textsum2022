from regex import R
import requests
from threading import Thread 
  
# api-endpoint
URL = "http://192.168.2.25:4100/primera"
   
a = [""" (CNN) Hurricane Harvey has claimed another victim, about two months after making landfall in Texas . \n \n A 31-year-old man died last week after being diagnosed with a rare flesh-eating bacterial infection known as necrotizing fasciitis, the Galveston County Health District announced Monday. \n \n The man has been identified as Josue Zurita, according to the Houston Chronicle , and he was helping repair several homes damaged by flooding from Harvey. \n \n Zurita went to the hospital on October 10 with a seriously infected wound on his upper left arm and was diagnosed with necrotizing fasciitis, according to the Galveston County Health District. \n \n In an obituary on the Galveston-based Carnes Brothers Funeral Home\'s website , Zurita was called a "loving father and hard-working carpenter" who moved to the United States from Mexico to help his family and "remained to help with the rebuilding after hurricane Harvey." \n \n Zurita\'s death follows that of Nancy Reed, a 77-year-old Houston-area woman who died...""" ,""" Josue "Cochito" Gedeon Perez Zurita September 01, 1986 - October 16, 2017 \n \n \n \n Share this obituary \n \n GALVESTON: Josue “Cochito” Gedeon Perez Zurita age 31 of Galveston died Monday, October 16, 2017 at Jennie Sealy Hospital in Galveston. Funeral services are 7:00pm Sunday, October 22, 2017 at Carnes Brothers Funeral Home in Galveston. Visitation will begin at 4:00pm with a rosary to be recited at 5:30pm. He will be laid to rest in his hometown of Miahuatlan, Oaxaca, Mexico. \n \n Josue was born on September 1, 1986 in Oaxaca, Mexico. He was a loving father and hard working carpenter. He moved to the United States to help his family. He remained to help with the rebuilding after hurricane Harvey that hit Harris and Galveston Counties. While working the current rebuilding efforts he was struck with an illness that claimed his life. He will be remembered as a loyal friend and devoted Christian father who remained faithful to his Catholic Faith. \n \n Survivors include his parents, Castulo Perez Reyes..."""
]

# defining a params dict for the parameters to be sent to the API
PARAMS = {"list_doc":a, 
            }
  
# sending get request and saving the response as response object

def run():
    r =  requests.post(url = URL, json = PARAMS)
    print(r)

    # print(r.content.json())
run()