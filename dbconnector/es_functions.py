from awsfunctions.bedrock_functions import get_embedding
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

def create_elasticsearch_client():
    """
    Create and return an Elasticsearch client using environment variables.
    
    Returns:
        Elasticsearch: Configured Elasticsearch client
    """
    load_dotenv()
    return Elasticsearch(
        [os.getenv("ES_URI")],  
        http_auth=(os.getenv("ES_USERNAME"), os.getenv("ES_PASSWORD")),
        verify_certs=False
    )





def extract_words_from_string(input_string):
    """
    Extract individual words from an input string.
    
    Args:
        input_string (str): The input text to split into words
        
    Returns:
        list: A list of words from the input string
    """
    return input_string.split()

def build_card_search_query(words, size=10):
    """
    Build an Elasticsearch query to match card names containing any of the given words.
    
    Args:
        words (list): List of words to search for in card names
        size (int): Maximum number of results to return
        
    Returns:
        dict: Elasticsearch query object
    """
    return {
        "size": size,  
        "query": {
            "bool": {
                "should": [
                    {"match": {"name": word}}
                    for word in words
                ]
            }
        }
    }

def get_card_index_name():
    """
    Get the card index name from environment variables.
    
    Returns:
        str: The name of the card index
    """
    load_dotenv()
    return os.getenv("ES_CARD_INDEX")

def execute_elasticsearch_query(index_name, query):
    """
    Execute a query against the Elasticsearch index.
    
    Args:
        index_name (str): The name of the index to search
        query (dict): The Elasticsearch query to execute
        
    Returns:
        dict: The Elasticsearch response
    """
    es = create_elasticsearch_client()
    return es.search(index=index_name, body=query)

def find_card_names_in_string(input_string):
    """
    Find card names in a string by searching the card index.
    
    Args:
        input_string (str): The input text that may contain card names
        
    Returns:
        dict: Elasticsearch response containing matching card documents
    """
    words = extract_words_from_string(input_string)
    query = build_card_search_query(words)
    index_name = get_card_index_name()
    response = execute_elasticsearch_query(index_name, query)
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
    vector_embedding = get_embedding(input_string)    
    query = get_vector_search_query(vector_embedding, top_k)

    response = execute_elasticsearch_query(index, query)
    return extract_and_format_hits(response)

def extract_hits_from_response(response):
    """
    Extracts hits from an Elasticsearch response.
    
    Args:
        response (dict): The Elasticsearch response
        
    Returns:
        list: A list of hit objects from the response
    """
    return response.get('hits', {}).get('hits', [])

def format_hit_to_vector(hit):
    """
    Formats a single Elasticsearch hit into a vector result.
    
    Args:
        hit (dict): A single hit from Elasticsearch results
        
    Returns:
        dict: A formatted dictionary with id, score, and source
    """
    return {
        'id': hit['_id'],
        'score': hit['_score'],
        'source': hit['_source']
    }

def extract_and_format_hits(response):
    """
    Extracts hits from an Elasticsearch response and formats them into vectors.
    
    Args:
        response (dict): The Elasticsearch response
        
    Returns:
        list: A list of formatted vector results
    """
    hits = extract_hits_from_response(response)
    return [format_hit_to_vector(hit) for hit in hits]

def get_vector_search_query(vector_embedding, top_k=3):
    """
    Constructs an Elasticsearch k-nearest neighbors (kNN) query for vector search.
    
    Args:
        vector_embedding (list): The vector embedding of the input text
        top_k (int): The number of closest vectors to retrieve (default: 3)
        
    Returns:
        dict: A dictionary containing the Elasticsearch kNN query configuration
    """
    return {
        "knn": {
            "field": "embedding",
            "query_vector": vector_embedding,
            "k": top_k,
            "num_candidates": top_k * 10  
        }
    }