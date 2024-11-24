from fastapi import FastAPI, Request
from awsfunctions.bedrock_functions import get_llm_answer

from questionenrichment.question_enricher import get_present_card_info



app = FastAPI()

@app.post("/answer")
async def answer_question(request: Request):
    data = await request.json()
    question = data.get("question")
    present_cards=get_present_card_info(question)
    return {"answer": get_llm_answer(question)}