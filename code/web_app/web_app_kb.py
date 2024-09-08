import boto3
import streamlit as st


class CONFIG:
    model_arn = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
    temperature = 0
    top_k = 200


@st.cache_resource
def get_bedrock_agent_client():
    return boto3.client(service_name="bedrock-agent-runtime", region_name="us-east-1")


def generate_response(prompt, kb_id):
    bedrock_agent_runtime_client = get_bedrock_agent_client()
    
    input_prompt = f""" 
    以下の質問に日本語で回答してください。
    【質問】
    {prompt}
    """
    
    generation_configuration = {
        "inferenceConfig": {
            "textInferenceConfig": {
                "maxTokens": 2048,  
                "temperature": CONFIG.temperature,  
                "stopSequences": ["Observation"],
            }
        },
        "additionalModelRequestFields": {"top_k": CONFIG.top_k},  
    }
    
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': input_prompt,
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': CONFIG.model_arn,
                "generationConfiguration": generation_configuration
            }
        }
    )

    return {"content":[{"text": response["output"]["text"]}], "role":"assistant"}


def display_history(messages):
    for message in st.session_state.messages:
        display_msg_content(message)


def display_msg_content(message):
    with st.chat_message(message["role"]):
        st.write(message["content"][0]["text"])

def get_parameter(name):
    ssm = boto3.client('ssm', region_name="us-east-1")
    param = ssm.get_parameter(Name=name,WithDecryption=True)
    return param['Parameter']['Value']


def main():
    
    kb_id = get_parameter("/cdkworkshop/kbid")
    st.title("Bedrock Conversation Application")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_history(st.session_state.messages)

    if prompt := st.chat_input("何かご用ですか?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        st.session_state.messages.append(input_msg)

        response_msg = generate_response(prompt, kb_id)
        display_msg_content(response_msg)
        st.session_state.messages.append(response_msg)


if __name__ == "__main__":
    main()