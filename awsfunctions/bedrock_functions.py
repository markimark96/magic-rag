from awsfunctions.aws_functions import get_aws_client
from langchain_aws import BedrockLLM
from dotenv import load_dotenv
import os
import boto3
import json



def get_llm_answer(question):
    load_dotenv()
    bedrock_client = get_aws_client("bedrock-runtime")
    llm = BedrockLLM(
        client=bedrock_client,
        model_id=os.getenv("LLM_MODEL_ID")  
    )
    response = llm.invoke(question)
    return response

def get_embedding(input_string):
    load_dotenv()
    aws_access_key = os.getenv("AWS_ACCES_KEY")
    aws_secret = os.getenv("AWS_SECRET")
    aws_region = os.getenv("AWS_REGION")
        # Initialize AWS Bedrock client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret
    )
    
    # Generate vector embedding for the input string using Amazon Titan model
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            'inputText': input_string
        })
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embedding']