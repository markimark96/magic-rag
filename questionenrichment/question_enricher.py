

from dbconnector.es_functions import find_card_names_in_string


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
    print(reduced_cardnames)
      
    
    
