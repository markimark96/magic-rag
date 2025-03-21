from awsfunctions.aws_functions import get_aws_client
from dotenv import load_dotenv
import os
import boto3
import json



def query_llm(prompt):
    client = get_aws_client("bedrock-runtime")  
    model_id = os.getenv("LLM_MODEL_ID")

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 10000})  
    )

    response_body = json.loads(response["body"].read().decode("utf-8"))
    return response_body.get("completion", "No response generated.")

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