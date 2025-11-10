from calendar import TUESDAY
from kafka import KafkaProducer,KafkaConsumer
import json 
from json import loads
def test():
    # consumer = KafkaConsumer(
    #     'test_tupk1',
    #     bootstrap_servers=["b-1.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092",
    #     "b-2.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092",
    #     "b-3.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092"],
    #     auto_offset_reset='earliest',
    #     # enable_auto_commit=True,
    #     max_poll_records=5,
    #     max_poll_interval_ms=600000,

    #     group_id='multinew-group',
    #     value_deserializer=lambda x: loads(x.decode('utf-8')))
    # f = open("/home/user01/Documents/API/Single_API/encode/encoded-20220727080145.txt", "r")
    # a = f.read()
    # f2 = open("/home/user01/Documents/API/Single_API/encode/encoded-20220727153816.txt", "r")
    # b = f2.read()
    a = '''The COVID-19 pandemic has highlighted the importance of hospitals abilities to  evaluate and care for an increased volume of patients exceeding normal  operating capacity, known as medical surge. All eight hospitals in GAOs review  reported multiple challenges related to staff, supplies, space, or information.  These are critical components for an effective medical surge response, according  to the Department of Health and Human Services (HHS). All eight hospitals  reported staffing challenges, such as a lack of staff to care for the increase in  sick patients or staff becoming ill and unable to work, affecting hospital services.  Hospitals took steps to address these challenges, such as supplementing staffing  levels where possible or training staff on proper personal protective equipment  use to prevent infection. Health care coalitionsgroups of health care and  response organizations in a defined geographic location supported by HHS  fundingaided hospitals. For example, they helped coordinate patient transfers  to balance hospital loads, obtain and distribute needed medical supplies, and  communicate hospital needs to their states.
    HHS has programs and activities underway intended to support medical surge  readiness for hospitals and other health care organizations, but it is too soon to  know the effectiveness of these efforts. For example, HHS implemented a new  medical surge exercise for coalitions in 2021 to test readiness, and plans to  establish targets to measure performance. It is also considering how to use the  findings and lessons learned from its 2021 assessment of coalitions during the  pandemic to improve its support of coalitions and their communities. HHS is also  funding the development of a regional disaster health response system, which  aims to develop effective approaches to medical surge response across multiple  states. This includes improving data sharing on resource and capacity issues,  and developing specialized teams that can respond to a range of hazards. HHS  is considering its next steps regarding the expansion of this regional system.  Further, HHS is developing regional guidelines for hospitals and other facilities  related to treating patients and increasing medical surge capacity during public  health emergencies as required by statute. Officials did not provide a date for  when the guidelines would be made publicly available.
    HHS leads the nation's medical and  public health preparedness for,  response to, and recovery from  emergencies and disasters. This  includes helping hospitals and others  build medical surge readiness.  Emergencies, such as the COVID-19  pandemic, put enormous strain on  hospitals in times of crisis.'''
    producer = KafkaProducer(bootstrap_servers='kafka-1:9092',
                value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    for i in range(10,15):
        doc = {
            "user_id":"11212",
            "sumary_id":i,
            "original_doc_ids": ["12122"],
            "documents":[
                {
                "documents_id":"12122",
                "raw_text":a,
                "file_type":0,
                "page_from": 0,
                "page_to" :10
                }],

            "topic": [],
            "id_mapAlgTypeAI" :[4,16],
            "percent_output": 0.3,
            "is_single": True
        }
        producer.send("single_root", doc)


test()