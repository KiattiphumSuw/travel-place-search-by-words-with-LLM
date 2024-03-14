import time
import csv
import weaviate
import weaviate.classes as wvc
import os
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv()

CLUSTER_URL = os.getenv('CLUSTER_URL')
WEAVIATE_AuthApiKey = os.getenv('WEAVIATE_AuthApiKey')
GPT_KEY1 = os.getenv('GPT_KEY1')
GPT_KEY2 = os.getenv('GPT_KEY2')
GPT_KEY3 = os.getenv('GPT_KEY3')

client1 = weaviate.connect_to_wcs(
        cluster_url=CLUSTER_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AuthApiKey),
        headers={
            "X-OpenAI-Api-Key": GPT_KEY1
        }
    )

client2 = weaviate.connect_to_wcs(
        cluster_url=CLUSTER_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AuthApiKey),
        headers={
            "X-OpenAI-Api-Key": GPT_KEY2
        }
    )

client3 = weaviate.connect_to_wcs(
        cluster_url=CLUSTER_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AuthApiKey),
        headers={
            "X-OpenAI-Api-Key": GPT_KEY3
        }
    )
clients = [client1, client2, client3]
shuold_wait = False
try:
    pass
    with open('test_review.json', 'r', encoding='utf-8') as file:
        data = json.load(file)  
        
    y = []
    y_pred = [] 
    count = 0
    selector = 0
    should_wait = False
    is_name = True
    for d in data:
        count += 1
        for _, v in d.items():
            if(is_name):
                res = v
                is_name = False
            else:
                re = v
                is_name = True
        print(f'''count : {count}
        res: {res}
        re: {re}
        ''')
        
        if(count%3 == 0):
            selector = (selector + 1)%3
            should_wait = True

        if(selector==0 and should_wait):
            print("Hi")
            time.sleep(70)
            should_wait = False
            
        questions = clients[selector].collections.get("Review")
        response = questions.query.near_text(
            query= re,
            limit= 2
        )

        y_temp = response.objects[0].properties["restaurants"]
        y_pred.append(y_temp)
        y += [res]
    
    print("==========================================================================")
    print(y)
    print("==========================================================================")
    print(y_pred)
    combined_data = list(zip(y, y_pred))
    # Specify the CSV file name
    csv_file = 'data/output.csv'

    # Write the data to the CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header
        writer.writerow(['y', 'y_pred'])
        
        # Write data
        writer.writerows(combined_data)

    print(f'CSV file "{csv_file}" created successfully.')

finally:
    for c in clients:    
        c.close()  