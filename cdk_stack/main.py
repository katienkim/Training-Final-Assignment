from aws_cdk import (
    Stack,
    aws_apigateway,
    aws_lambda,
    aws_s3 as s3,
    Duration
)
from constructs import Construct
# CDK Labs library import for bedrock implementation
from cdklabs.generative_ai_cdk_constructs import (
    bedrock
)

class PyRestApiStack(Stack):
    def __init__(self, scope = Construct, construct_id = str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create s3 bucket that stores HR related documents
        s3_bucket = s3.Bucket(
            self,
            "HRDocsBucket",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # Create s3 vector bucket that stores chunks of embedded HR document data
        # s3_vector = s3.Bucket(
        #     self,
        #     "HRVectorBucket"
        # )

        # Create knowledge base using Bedrock
        # Use Bedrock Titan as the embedding model
        # Use existing s3 vectorstore as the vector store for knowledge base
        knowledge_base = bedrock.VectorKnowledgeBase(
            self,
            "HRKnowledgeBase",
            embeddings_model=bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024
        )

        # Attach existing s3 document bucket as data source for knowledge base
        knowledge_base.add_s3_data_source(
            bucket=s3_bucket,
            chunking_strategy= bedrock.ChunkingStrategy.semantic(
                buffer_size=0,
                breakpoint_percentile_threshold=95,
                max_tokens=300
            )
        )

        claude_model = bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V2_0
        
        # Create lambda function 
        hr_lambda = aws_lambda.Function(
            self,
            "HRLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_13,
            code=aws_lambda.Code.from_asset("cdk_stack/services"),
            handler="index.lambda_handler",
            timeout=Duration.seconds(60),
            environment={
                "KNOWLEDGE_BASE_ID": knowledge_base.knowledge_base_id,
                "MODEL_ID": claude_model.model_id
            }
        )

        # Grants lambda permissions to retrieve and retrieve+generate the knowledge base
        knowledge_base.grant_query(hr_lambda)
        # Grants lambda permissions to invoke the claude model in the current region
        claude_model.grant_invoke(hr_lambda)

        # Create api gateway and its subroute
        api = aws_apigateway.RestApi(self, "hr-api")
        hr_resource = api.root.add_resource("hr")

        # Create lambda integration attach to api gateway
        # Add get and post methods to the lambda function
        hr_lambda_integration = aws_apigateway.LambdaIntegration(hr_lambda)
        hr_resource.add_method("POST", hr_lambda_integration)