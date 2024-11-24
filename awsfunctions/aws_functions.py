import boto3
from dotenv import load_dotenv
import os

def get_aws_client(service):
    load_dotenv()
    client = boto3.client(
        service_name=service,
        region_name=os.getenv("AWS_REGION"),  
        aws_access_key_id=os.getenv("AWS_ACCES_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET")
    )
    return client