from awsfunctions.bedrock_functions import get_embedding
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

def get_closest_vectors(input_string, index, top_k=3):
    """
    Retrieves the top_k closest vectors from the Elasticsearch rules index
    to the input string using the amazon.titan-embed-text-v1 model.
    
    Args:
        input_string (str): The input text to find similar vectors for
        top_k (int): The number of closest vectors to retrieve (default: 3)
        
    Returns:
        list: A list of dictionaries containing the closest vectors with their scores
    """
    
    # Get environment variables
    vector_embedding = get_embedding(input_string)    
    # Construct the Elasticsearch query for vector search
    query = {
        "knn": {
            "field": "embedding",
            "query_vector": vector_embedding,
            "k": top_k,
            "num_candidates": top_k * 10  # Optional: adjust based on your use case
        }
    }


    
    # Send the query to Elasticsearch
    response = es.search(index=index, body=query)
    
    # Process the response
    hits = response.get('hits', {}).get('hits', [])
    
    closest_vectors = []
    for hit in hits:
        closest_vectors.append({
            'id': hit['_id'],
            'score': hit['_score'],
            'source': hit['_source']
        })
    
    return closest_vectors