import json
import boto3
import os

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')

### Create Lambda handler method:
# event (param): data payload that triggers Lambda function
# context (param): runtime information
def lambda_handler(event, context):
    # Log the incoming event for debugging
    print(f"Received event: {json.dumps(event)}")

    try:
        KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID')
        MODEL_ID = os.environ.get('MODEL_ID')

        # Check for existence of KNOWLEDGE_BASE_ID and MODEL_ID
        if not KNOWLEDGE_BASE_ID or not MODEL_ID:
            raise ValueError("Missing KNOWLEDGE_BASE_ID or MODEL_ID environment variables.")
  
        body = json.loads(event['body'])
        user_query = body.get('query', '')

        # Check for query input in the data payload
        if not user_query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query parameter is missing.'})
            }

        print(f"Received query: {user_query}")
        
        # --- STEP 1: RETRIEVE context from the Knowledge Base ---
        print("Retrieving context from Knowledge Base...")
        retrieval_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={
                'text': user_query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5  # Retrieve top 5 relevant chunks
                }
            }
        )
        
        retrieval_results = retrieval_response.get('retrievalResults', [])
        
        # Extract context and source references from the retrieval results
        context = ""
        source_references = []
        for result in retrieval_results:
            context += result['content']['text'] + "\n"
            source_references.append(result['location']['s3Location']['uri'])

        print(f"Retrieved context: {context[:500]}...") # Log first 500 chars of context
        
        # --- STEP 2: GENERATE an answer using the retrieved context ---
        print("Generating answer with Claude 4...")

        # Create the prompt for the language model
        prompt = f"""
        Human: You are an expert HR assistant. Using the following context, answer the user's question.
        Provide a direct answer and cite the sources you used. Do not use information outside the context.

        <context>
        {context}
        </context>

        <question>
        {user_query}
        </question>

        Assistant:
        """
        
        # Body for the Claude 4 Sonnet model (same for Claude 3 and 3.5)
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }
        
        # Invoke the model
        generation_response = bedrock_runtime.invoke_model(
            body=json.dumps(request_body),
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(generation_response['body'].read())
        answer = response_body['content'][0]['text']

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' 
            },
            'body': json.dumps({
                'answer': answer,
                'sources': list(set(source_references)) # Return unique sources
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'error': str(e)})
        }
