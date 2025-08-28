# import json
# import boto3
# import os

# bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

# def lambda_handler(event, context):
#     # Log the incoming event for debugging
#     print(f"Received event: {json.dumps(event)}")

#     try:
#         KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID')
#         MODEL_ID = os.environ.get('MODEL_ID')

#         if not KNOWLEDGE_BASE_ID or not MODEL_ID:
#             raise ValueError("Missing KNOWLEDGE_BASE_ID or MODEL_ID environment variables.")
  
#         body = json.loads(event['body'])
#         user_query = body.get('query', '')

#         if not user_query:
#             return {
#                 'statusCode': 400,
#                 'body': json.dumps({'error': 'Query parameter is missing.'})
#             }

#         print(f"Received query: {user_query}")
#         response = bedrock_agent_runtime.retrieve_and_generate(
#             input={
#                 'text': user_query
#             },
#             retrieveAndGenerateConfiguration={
#                 'type': 'KNOWLEDGE_BASE',
#                 'knowledgeBaseConfiguration': {
#                     'knowledgeBaseId': KNOWLEDGE_BASE_ID,
#                     'modelArn': f"arn:aws:bedrock:us-west-2::foundation-model/{MODEL_ID}"
#                 }
#             }
#         )

#         # Extract the generated response text and source citations
#         answer = response['output']['text']
#         citations = []
        
#         if 'citations' in response:
#             for citation in response['citations']:
#                 if 'retrievedReferences' in citation:
#                     for ref in citation['retrievedReferences']:
#                         if 'content' in ref and 'text' in ref['content']:
#                             citations.append(ref['content']['text'])
                       
#                         if 'location' in ref and 's3Location' in ref['location']:
#                              s3_loc = ref['location']['s3Location']
#                              citations.append(f"Source: s3://{s3_loc['uri']}") 
#         return {
#             'statusCode': 200,
#             'headers': {
#                 'Content-Type': 'application/json',
#                 'Access-Control-Allow-Origin': '*' 
#             },
#             'body': json.dumps({
#                 'query': user_query,
#                 'answer': answer,
#                 'citations': citations
#             })
#         }

#     except Exception as e:
#         print(f"Error: {e}")
#         return {
#             'statusCode': 500,
#             'headers': {
#                 'Content-Type': 'application/json',
#                 'Access-Control-Allow-Origin': '*'
#             },
#             'body': json.dumps({'error': str(e)})
#         }