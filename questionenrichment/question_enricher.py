

import requests
from dbconnector.es_functions import find_card_names_in_string, get_closest_vectors
import os
from dotenv import load_dotenv

def get_present_card_info(question):
    potentional_present_card_names = find_card_names_in_string(question)
    cards=[]
    #Get all card names present in the question
    if 'hits' in potentional_present_card_names and 'hits' in potentional_present_card_names['hits']:
        for hit in potentional_present_card_names['hits']['hits']:
            name = hit.get('_source', {}).get('name', '')
            if name and name.lower() in question.lower():   
                cards.append(hit['_source'])
    sorted_cardnames=sorted(cards, key=lambda x: len(x.get('name', '')), reverse=True)
    #Reduce the card names to contain only the longest match
    reduced_cardnames = []
    for obj in sorted_cardnames:
        if not any(obj.get('name', '') in other_obj.get('name', '') for other_obj in reduced_cardnames):
            reduced_cardnames.append(obj)
    # print(reduced_cardnames)
    return reduce_card_fields(reduced_cardnames)

def reduce_card_fields(cards):
    reduced_cards = []
    for card in cards:
        name = card.get('name')
        oracle_text = card.get('oracle_text')
        rulings_uri = card.get('rulings_uri')

        # Attempt to fetch the rulings content from the rulings_uri
        try:
            response = requests.get(rulings_uri)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            rulings_data = response.json().get("data", [])  # Extract rulings list
            rulings_comments = [ruling.get("comment") for ruling in rulings_data]  # Extract only comments
        except Exception as e:
            rulings_comments = [f"Error fetching rulings: {e}"]
        
        reduced_cards.append({
            'name': name,
            'oracle_text': oracle_text,
            'rulings': rulings_comments  # Store only the list of comments
        })
    
    return reduced_cards
      
def get_relevant_data(user_input,index):
    releveant_data = []
    load_dotenv()
    data_index = os.getenv(index)
    results = get_closest_vectors(user_input,data_index)
    for idx, result in enumerate(results):
        content = result['source'].get('content', 'No content available')
        releveant_data.append(content)    
    return releveant_data


def get_full_prompt(present_cards,relevant_questions,relevant_rules,user_input):
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


Given the abow context try to answer this question:
{user_input}


Assistant:
"""
    
