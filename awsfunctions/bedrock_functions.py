from langchain_aws import BedrockLLM
from dotenv import load_dotenv
import os

from awsfunctions.aws_functions import get_aws_client


def get_llm_answer(question):
    load_dotenv()
    bedrock_client = get_aws_client("bedrock-runtime")
    llm = BedrockLLM(
        client=bedrock_client,
        model_id=os.getenv("LLM_MODEL_ID")  
    )
    response = llm.invoke(question)
    return response
