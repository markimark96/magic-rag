import boto3
from langchain_aws import BedrockLLM
from dotenv import load_dotenv
import os

load_dotenv()


bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_REGION"),  
    aws_access_key_id=os.getenv("AWS_ACCES_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET")
)


llm = BedrockLLM(
    client=bedrock_client,
    model_id=os.getenv("LLM_MODEL_ID")  
)

question = "What is the capital of Hungary?"
response = llm.invoke(question)

print("Response:", response)
