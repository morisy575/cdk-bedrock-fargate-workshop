from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ssm as ssm
)
from cdklabs.generative_ai_cdk_constructs import (
    bedrock,
    opensearchserverless,
    opensearch_vectorindex
)
from constructs import Construct


class KbStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # The code that defines your stack goes here
        
        vector_store = opensearchserverless.VectorCollection(self, 'VectorCollection',
            collection_name = 'cdk-bedrock-workshop-collection',
            standby_replicas = opensearchserverless.VectorCollectionStandbyReplicas.DISABLED
        )
        
        vector_index = opensearch_vectorindex.VectorIndex(self, 'VectorIndex',
            collection = vector_store,
            index_name = 'cdk-bedrock-workshop-vector-index',
            vector_dimensions = 1024,
            vector_field = 'bedrock-knowledge-base-default-vector',
            mappings= [
                opensearch_vectorindex.MetadataManagementFieldProps(
                    mapping_field='AMAZON_BEDROCK_TEXT_CHUNK',
                    data_type='text',
                    filterable=True
                ),
                opensearch_vectorindex.MetadataManagementFieldProps(
                    mapping_field='AMAZON_BEDROCK_METADATA',
                    data_type='text',
                    filterable=False
                )
            ],
        )
        
        kb = bedrock.KnowledgeBase(self, 'KnowledgeBase',
            vector_store = vector_store,
            vector_index = vector_index,
            index_name = 'cdk-bedrock-workshop-vector-index',
            embeddings_model= bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
            instruction=  'ユーザーからの質問に回答するためにこのナレッジベースを利用してください。'
        )
        
        doc_bucket = s3.Bucket(self, 'DockBucket', 
            bucket_name="cdk-bedrock-workshop-<your name>-bucket",
            versioned=True
        )
        
        data_source = bedrock.S3DataSource(self, 'DataSource',
            bucket= doc_bucket,
            knowledge_base=kb,
            data_source_name='datasource-1',
            chunking_strategy= bedrock.ChunkingStrategy.FIXED_SIZE,
            max_tokens=512,
            overlap_percentage=20
        )
        
        ssm.StringParameter(self, "CdkWSParameterKbId",
            parameter_name="/cdkworkshop/kbid",
            string_value=kb.knowledge_base_id
        )