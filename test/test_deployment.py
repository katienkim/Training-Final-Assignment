import os
import requests
import json

API_ENDPOINT_URL = os.environ.get("API_ENDPOINT_URL", "https://c99i1dn479.execute-api.us-west-2.amazonaws.com/prod/hr")

# Prompts for the LLM through the RAG pipeline
prompts = ["What is the vacation policy?",
            "How do I request time off?",
            "What are the office hors?"
           ]

def test_rag():
    # Test to see if API_ENDPOINT_URL was defined
    if "YOUR_API_ENDPOINT_URL_HERE" in API_ENDPOINT_URL:
        print("ERROR: Please set the API_ENDPOINT_URL in this script.")
        return

    headers = {
        'Content-Type': 'application/json'
    }
    # For each prompt in prompt list, set query as the prompt
    # Call for the API Gateway endpoint and retrieve a response
    # Print the response or throw an exception for any error
    for prompt in prompts:
        payload = {
            'query': prompt
        }
        try:
            # Call the deployed API Gateway endpoint
            response = requests.post(API_ENDPOINT_URL, headers=headers, data=json.dumps(payload), timeout=300)
            response.raise_for_status()  # Raise an exception for bad status codes

            response_data = response.json()
                    
            # Print the response from the Lambda function
            print(f"Answer: {response_data.get('answer')}")
            print(f"Sources: {response_data.get('sources')}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_rag()
