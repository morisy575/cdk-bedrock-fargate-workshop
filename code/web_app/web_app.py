import boto3
import streamlit as st


class CONFIG:
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    system_prompt = "あなたは優秀なチャットAIアシスタントです。"
    temperature = 0.5
    top_k = 200


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


def generate_response(messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": CONFIG.system_prompt}]

    inference_config = {"temperature": CONFIG.temperature}
    additional_model_fields = {"top_k": CONFIG.top_k}

    response = bedrock_client.converse(
        modelId=CONFIG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
    )

    return response["output"]["message"]


def display_history(messages):
    for message in st.session_state.messages:
        display_msg_content(message)


def display_msg_content(message):
    with st.chat_message(message["role"]):
        st.write(message["content"][0]["text"])


def main():
    st.title("Bedrock Conversation Application")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_history(st.session_state.messages)

    if prompt := st.chat_input("何かご用ですか?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        st.session_state.messages.append(input_msg)

        response_msg = generate_response(st.session_state.messages)
        display_msg_content(response_msg)
        st.session_state.messages.append(response_msg)


if __name__ == "__main__":
    main()