from pynvml import *
import requests
nvmlInit()
import random
import time

list_algo = ["http://192.168.2.25:8100/MemSum", "http://192.168.2.25:7100/presum"]
with open("1.txt", "r") as r:
    d1 = r.read()

with open("2.txt", "r") as r:
    d2 = r.read()

with open("3.txt", "r") as r:
    d3 = r.read()

with open("4.txt", "r") as r:
    d4 = r.read()

texts =[d1,d2,d3,d4]

for al in list_algo:
    print(f"Thuat toan: {al}")
    time.sleep(2)
    h = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(h)
    print(f'total    : {info.used // 1024 ** 2}')
    for i in range(501):
        text = texts[random.randint(0,3)]
        result = requests.post(url = al, json={"text":text, "percent_output":0.3})
        h = nvmlDeviceGetHandleByIndex(0)
        info = nvmlDeviceGetMemoryInfo(h)
        if i==0:
            time.sleep(2)
            print(f'total after {i} interation   : {info.used // 1024 ** 2}')
        if i==100:
            time.sleep(2)
            print(f'total after {i} interation   : {info.used // 1024 ** 2}')
        if i==300:
            time.sleep(2)
            print(f'total after {i} interation   : {info.used // 1024 ** 2}')
        if i==500:
            time.sleep(2)
            print(f'total after {i} interation   : {info.used // 1024 ** 2}')



