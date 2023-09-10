from pathlib import Path

from langchain.chat_models import ChatOpenAI

from ghostcoder.callback import LogCallbackHandler
from ghostcoder.llm import ChatLLMWrapper
from ghostcoder.llm.wizardcoder import WizardCoderLLMWrapper


def create_openai_client(log_dir: Path, llm_name: str, temperature: float):
    callback = LogCallbackHandler(str(log_dir))
    return ChatLLMWrapper(ChatOpenAI(
        model=llm_name,
        temperature=temperature,
        callbacks=[callback]
    ))

def create_testgen_client(log_dir: Path, llm_name: str, temperature: float):
    from langchain.llms import TextGen
    callback = LogCallbackHandler(str(log_dir))
    return WizardCoderLLMWrapper(llm=TextGen(
        model_url="http://43.230.163.163:23086",
        max_new_tokens=750,
        preset="simple-1",
        #temperature=temperature,
        #top_p=0.2,
        #top_k=40,
        do_sample=True,
        callbacks=[callback]))
