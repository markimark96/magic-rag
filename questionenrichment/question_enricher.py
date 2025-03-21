import requests
from dbconnector.es_functions import find_card_names_in_string, get_closest_vectors
import os
from dotenv import load_dotenv

def get_present_card_info(question):
    """Main function to identify card names in a question and return their details including oracle text and rulings.
    
    Args:
        question (str): The user's question containing potential card names
        
    Returns:
        list: A list of dictionaries containing card details with name, oracle_text, and rulings
    """
    search_response = find_card_names_in_string(question)
    hits = extract_card_hits(search_response)
    cards = filter_cards_present_in_question(hits, question)
    sorted_cards = sort_cards_by_name_length(cards)
    reduced_cards = filter_for_longest_names(sorted_cards)
    return reduce_card_fields(reduced_cards)

def get_relevant_data(user_input, index):
    """Main function to retrieve relevant data based on user input from the vector store.
    
    Args:
        user_input (str): The user's question or input text
        index (str): The environment variable name for the Elasticsearch index
        
    Returns:
        list: A list of relevant content extracted from the vector store search results
    """
    data_index = load_index_from_env(index)
    results = fetch_vector_results(user_input, data_index)
    return extract_content_from_results(results)

def extract_card_hits(search_response):
    """Extract hits from the search response.
    
    Args:
        search_response (dict): The response from Elasticsearch search
        
    Returns:
        list: A list of hit objects from the search response
    """
    if 'hits' in search_response and 'hits' in search_response['hits']:
        return search_response['hits']['hits']
    return []

def filter_cards_present_in_question(hits, question):
    """Filter hits to only include cards whose names are in the question.
    
    Args:
        hits (list): List of hit objects from Elasticsearch
        question (str): The user's question
        
    Returns:
        list: Filtered list of card objects whose names appear in the question
    """
    cards = []
    for hit in hits:
        name = hit.get('_source', {}).get('name', '')
        if name and name.lower() in question.lower():
            cards.append(hit['_source'])
    return cards

def sort_cards_by_name_length(cards):
    """Sort cards by name length in descending order.
    
    Args:
        cards (list): List of card objects
        
    Returns:
        list: Sorted list of card objects by name length (longest first)
    """
    return sorted(cards, key=lambda x: len(x.get('name', '')), reverse=True)

def filter_for_longest_names(sorted_cards):
    """Filter cards to only include those with the longest unique names.
    
    Args:
        sorted_cards (list): List of card objects sorted by name length
        
    Returns:
        list: Filtered list containing only cards with unique longest names
    """
    reduced_cardnames = []
    for obj in sorted_cards:
        if not any(obj.get('name', '') in other_obj.get('name', '') for other_obj in reduced_cardnames):
            reduced_cardnames.append(obj)
    return reduced_cardnames

def fetch_rulings(rulings_uri):
    """Fetch rulings from the provided URI and extract comments.
    
    Args:
        rulings_uri (str): URI to fetch rulings from
        
    Returns:
        list: List of ruling comments or error message
    """
    try:
        response = requests.get(rulings_uri)
        response.raise_for_status()
        rulings_data = response.json().get("data", [])
        return [ruling.get("comment") for ruling in rulings_data]
    except Exception as e:
        return [f"Error fetching rulings: {e}"]

def extract_card_fields(card):
    """Extract relevant fields from a card object.
    
    Args:
        card (dict): Card object with full details
        
    Returns:
        dict: Dictionary containing only name, oracle_text, and rulings
    """
    return {
        'name': card.get('name'),
        'oracle_text': card.get('oracle_text'),
        'rulings': fetch_rulings(card.get('rulings_uri'))
    }

def reduce_card_fields(cards):
    """Transform a list of cards into a list with only the relevant fields.
    
    Args:
        cards (list): List of card objects to transform
        
    Returns:
        list: List of dictionaries containing only name, oracle_text, and rulings
    """
    return [extract_card_fields(card) for card in cards]

def load_index_from_env(index_env_var):
    """Load the index name from environment variables.
    
    Args:
        index_env_var (str): Name of the environment variable containing the index name
        
    Returns:
        str: The index name from environment variables
    """
    load_dotenv()
    return os.getenv(index_env_var)

def fetch_vector_results(user_input, index_name):
    """Fetch the closest vector results from Elasticsearch.
    
    Args:
        user_input (str): The user's question or input text
        index_name (str): Name of the Elasticsearch index to search
        
    Returns:
        list: List of closest vector results
    """
    return get_closest_vectors(user_input, index_name)

def extract_content_from_results(results):
    """Extract content from vector search results.
    
    Args:
        results (list): List of vector search result objects
        
    Returns:
        list: List of content strings extracted from the results
    """
    relevant_data = []
    for idx, result in enumerate(results):
        content = result['source'].get('content', 'No content available')
        relevant_data.append(content)
    return relevant_data


def get_full_prompt(present_cards, relevant_questions, relevant_rules, user_input):
    """Create a comprehensive prompt for the LLM with all gathered information.
    
    This function combines card information, relevant rules, similar questions,
    and the user's input into a structured prompt for the language model.
    The prompt instructs the model to act as a Magic the Gathering judge
    and answer based on the provided context.
    
    Args:
        present_cards (str): JSON string containing information about cards mentioned in the question
        relevant_questions (list): List of similar questions and answers from forums
        relevant_rules (list): List of relevant game rules that may apply to the question
        user_input (str): The original question from the user
        
    Returns:
        str: A formatted prompt string ready to be sent to the language model
    """
    return f"""
Human:
You are a Magic the Gathering judge, who is expert in the games rules, but always tries to answer according to the data that is given to him.
Given this context try to answer the question below. Only answer if the context contains relevant information, else say that you dont have enough information and please give a more elaborate question.
It may be the case that some parts of the context is irrelevant to the question. In this case just ignore it!

Here are 3 rules that may or may not be relevant for you:
{relevant_rules}


Here are 3 questions with their answer from a forum that may or may not be relevant to you:
{relevant_questions}


Here are the cards with their rulings that are present in the question:
{present_cards}


Given the above context try to answer this question:
{user_input}


Assistant:
"""
    
