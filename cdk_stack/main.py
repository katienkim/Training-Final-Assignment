from aws_cdk import (
    Stack,
    aws_apigateway,
    aws_lambda,
    aws_s3 as s3,
    aws_iam as iam,
    Duration
)
from constructs import Construct
# CDK Labs library import for high level bedrock implementation
from cdklabs.generative_ai_cdk_constructs import (
    bedrock
)

### Create Rest API stack class that defines:
# S3 bucket for HR policy documents
# Bedrock Knowledge Base as a vector store
# Bedrock Titan Embed V2 as embedding model 
# Lambda function attached to API Gateway and LLM
# API Gateway for user prompting
# Anthropic's Claude Sonnet 4 as LLM 
class PyRestApiStack(Stack):
    def __init__(self, scope = Construct, construct_id = str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket that stores HR related documents
        s3_bucket = s3.Bucket(
            self,
            "HRDocsBucket",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )
        # Create Knowledge Base using Bedrock
        # Use Bedrock Titan as the embedding model
        # Use default vector store provided by Bedrock for Knowledge Base
        knowledge_base = bedrock.VectorKnowledgeBase(
            self,
            "HRKnowledgeBase",
            embeddings_model=bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024
        )

        # Attach existing S3 document bucket as data source for Knowledge Base
        # Semantic chunking for higher accuracy
        knowledge_base.add_s3_data_source(
            bucket=s3_bucket,
            # chunking_strategy= bedrock.ChunkingStrategy.fixed_size(
            #     overlap_percentage=10, 
            #     max_tokens=300
            # )
            chunking_strategy= bedrock.ChunkingStrategy.semantic(
                breakpoint_percentile_threshold=95, 
                buffer_size=0, 
                max_tokens=300
            )
        )

        # Create lambda function and initialize handler
        hr_lambda = aws_lambda.Function(
            self,
            "HRLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("cdk_stack/services"), # sets the lambda handler code
            handler="index.lambda_handler",
            timeout=Duration.seconds(60),
            # initialize environment variables for knowledge base id and llm model id
            environment={
                "KNOWLEDGE_BASE_ID": knowledge_base.knowledge_base_id,
                "MODEL_ID": "anthropic.claude-sonnet-4-20250514-v1:0"
            }
        )

        # Grants lambda permissions to retrieve and retrieve+generate the knowledge base
        knowledge_base.grant_query(hr_lambda)
        # Grants lambda role policy to invoke the claude model in the current region
        hr_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=[f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-sonnet-4-20250514-v1:0"]
            )
        )

        # Create API Gateway and its subroute
        api = aws_apigateway.RestApi(self, "hr-api")
        hr_resource = api.root.add_resource("hr")

        # Create lambda integration attach to API Gateway
        # Add get methods to the lambda integration
        hr_lambda_integration = aws_apigateway.LambdaIntegration(hr_lambda)
        hr_resource.add_method("POST", hr_lambda_integration)