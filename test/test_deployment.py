import boto3
import os
import requests
import json

s3 = boto3.client("s3")
lambda_client = boto3.client("lambda")
apigateway = boto3.client("apigatewayv2")

bucket_name = "HRDocsBucket"
lambda_name = "HRLambda"
API_ENDPOINT_URL = "https://c99i1dn479.execute-api.us-west-2.amazonaws.com/prod/"
AWS_REGION = "us-west-2"

TEST_QUESTION = "How many sick days does the company give?"


def upload_pdf_to_s3(bucket_name, file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found. Cannot upload.")
        return False
        
    print(f"\nUploading '{file_path}' to S3 bucket '{bucket_name}'...")
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    try:
        s3_client.upload_file(file_path, bucket_name, os.path.basename(file_path))
        print("✅ Upload successful.")
        return True
    except Exception as e:
        print(f"❌ Error uploading file to S3: {e}")
        return False
    
def query_api_endpoint(api_url, question):
    """
    Sends a POST request with a question to the API Gateway endpoint.
    
    Args:
        api_url (str): The full URL of the API Gateway endpoint.
        question (str): The question to send in the request body.
    """
    print(f"\nQuerying API endpoint with question: '{question}'...")
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'query': question
    }
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=300)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        print("✅ API query successful.")
        response_data = response.json()
        
        print("\n--- Bedrock Response ---")
        print(f"Answer: {response_data.get('response')}")
        print(f"Sources: {response_data.get('sources')}")
        print("------------------------\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"❌ An error occurred while querying the API: {e}")

def query_api_endpoint(api_url, question):
    """
    Sends a POST request with a question to the API Gateway endpoint.
    
    Args:
        api_url (str): The full URL of the API Gateway endpoint.
        question (str): The question to send in the request body.
    """
    print(f"\nQuerying API endpoint with question: '{question}'...")
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'query': question
    }
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=300)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        print("✅ API query successful.")
        response_data = response.json()
        
        print("\n--- Bedrock Response ---")
        print(f"Answer: {response_data.get('response')}")
        print(f"Sources: {response_data.get('sources')}")
        print("------------------------\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"❌ An error occurred while querying the API: {e}")

def main():
    query_api_endpoint(API_ENDPOINT_URL, TEST_QUESTION)