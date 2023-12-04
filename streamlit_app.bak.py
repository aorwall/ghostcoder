import logging
import os
from datetime import time

import openai
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

from ghostcoder import Ghostcoder
from ghostcoder.schema import TextItem

# openai.api_key = st.secrets["OPENAI_API_KEY"]


logging_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)
logging.getLogger('ghostcoder').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

class StreamHandler(BaseCallbackHandler):

    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")

with st.sidebar:
    #openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    repo_dir = st.text_input("Repository Directory", key="repo_dir", value=os.environ.get('REPO_DIR', ''))
    model_name = st.text_input("Model name", key="model_name", value=os.environ.get('MODEL_NAME', 'gpt-4-1106-preview'))
    debug_mode = st.toggle('Debug mode', True)

    if "ghostcoder" not in st.session_state:
        init_button = st.button("Load")
    else:
        init_button = st.button("Reload")

        ability_options = [("Auto", None), ("Investigate", "investigate"), ("Write code", "write_code")]
        ability = st.radio("Select Ability:",
                                   ability_options,
                                   format_func=lambda x: x[0],
                                   captions=[
                                       "Automatically select ability based on the prompt.",
                                       "Find files and answer questions about the code base.",
                                       "Write and save code to the repository."]
                                   )

        search_limit = number = st.number_input('File search hits', value=10, min_value=0, max_value=50)

        file_type = st.radio(
            "File types",
            ["All files", "Code", "Tests"])

        #show_filesystem = st.toggle('Show filesystem', True)

        new_file = st.text_input("File path")

        if st.button("Add file to context"):
            if new_file:
                st.session_state.ghostcoder.add_file_to_context(new_file)
                st.rerun()

        st.caption(f'**{st.session_state.ghostcoder.get_file_context_tokens()}** tokens in file context.')

        for idx, item in enumerate(st.session_state.ghostcoder.get_file_context()):
            col1, col2 = st.columns([4, 1])
            col1.write(item)
            if col2.button(f"X", key=f"remove_{idx}"):
                st.session_state.ghostcoder.remove_file_from_context(item)
                st.rerun()

if init_button:
    if repo_dir: # openai_api_key and
        st.session_state.messages = []

        with st.spinner('Indexing repository...'):
            st.session_state.ghostcoder = Ghostcoder(repo_dir=repo_dir, debug_mode=debug_mode, model_name=model_name)

        # Set OpenAI API key
        # openai.api_key = openai_api_key
        st.success("The repository was indexed successfully!")
        st.rerun()
    else:
        st.error("Please enter Repository Directory.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about anything"):
    if "ghostcoder" not in st.session_state:
        st.error("Please index the repository first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    message_placeholder = st.empty()
    stream_handler = StreamHandler(message_placeholder, display_method='write')

    content_type = None
    if file_type == "Code":
        content_type = "code"
    elif file_type == "Tests":
        content_type = "test"

    response = st.session_state.ghostcoder.request(prompt,
                                                   callback=stream_handler,
                                                   ability=ability,
                                                   content_type=content_type,
                                                   search_limit=search_limit,)

    for message in response:
        st.session_state.messages.append({"role": "assistant", "content": str(message)})

    st.rerun()
