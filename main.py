from fastapi import FastAPI, Request
import json
from awsfunctions.bedrock_functions import  query_llm

from questionenrichment.question_enricher import get_full_prompt, get_present_card_info, get_relevant_data



app = FastAPI()

@app.post("/answer")
async def answer_question(request: Request):
    data = await request.json()
    input_text = data.get("question")
    present_cards=get_present_card_info(input_text)
    cards_json = json.dumps(present_cards, indent=4)
    questions = get_relevant_data(input_text,"ES_QUESTION_INDEX")
    rules = get_relevant_data(input_text,"ES_RULE_INDEX")
    prompt = get_full_prompt(cards_json,questions,rules,input_text)
    answer = query_llm(prompt)
    print(prompt)
    print("==================================================================================================================")
    print(answer)
    return {"answer": answer}

