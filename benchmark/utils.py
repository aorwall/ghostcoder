from pathlib import Path

from langchain.chat_models import ChatOpenAI

from ghostcoder.callback import LogCallbackHandler
from ghostcoder.llm import ChatLLMWrapper


def create_openai_client(log_dir: Path, llm_name: str, temperature: float):
    callback = LogCallbackHandler(str(log_dir))
    return ChatLLMWrapper(ChatOpenAI(
        model=llm_name,
        temperature=temperature,
        callbacks=[callback]
    ))

