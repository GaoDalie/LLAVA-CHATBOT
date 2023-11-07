import streamlit as st
import replicate
from dotenv import load_dotenv

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")
load_dotenv()

# Here, if the replicate library has a method to set the token, use it. For example:
# replicate.set_auth_token(replicate_api)

with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['llava-13b'], key='selected_model')
    if selected_model == 'llava-13b':
        llm = 'yorickvp/llava-13b:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591'
    
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)

    st.markdown('📖 Learn how to build this app in this [blog](#link-to-blog)!')
# Add file uploader for images
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Function to generate LLaMA2 response
def generate_llava_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            if dict_message.get("type") == "image":
                string_dialogue += "User: [Image]\\n\\n"
            else:
                string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    output = replicate.run(llm, 
                           input={"image": uploaded_file, "prompt": prompt})
    return output

# Ensure session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"])
        else:
            st.write(message["content"])

# Sidebar to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Text input for chat
prompt = st.text_input("Type a message:")

# Button to send the message/image
if st.button('Send'):
    if uploaded_file:
        # If an image is uploaded, store it in session_state
        st.session_state.messages.append({"role": "user", "content": uploaded_file, "type": "image"})
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate a new response if the last message is not from the assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llava_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
