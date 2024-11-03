from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()
es = Elasticsearch(
    [os.getenv("ES_URI")],  # Replace with your Elasticsearch server address
    http_auth=(os.getenv("ES_USERNAME"), os.getenv("ES_PASSWORD")),
    verify_certs=False
)
index_name=os.getenv("ES_CARD_INDEX")



def find_card_names_in_string(input_string):
    words = input_string.split()
    
    # Construct a query to match documents where the name field contains any of the words
    query = {
        "size": 10,  
        "query": {
            "bool": {
                "should": [
                    {"match": {"name": word}}
                    for word in words
                ]
            }
        }
    }
        
    response = es.search(index=index_name, body=query)
    return response