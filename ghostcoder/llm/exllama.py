from __future__ import annotations

import glob
import logging
import os
from typing import Any, Dict,  List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from pydantic import Field, root_validator

logger = logging.getLogger(__name__)


class Exllama(LLM):
    llm: Any  #: :meta private:
    tokenizer: Any  #: :meta private:

    model_directory: str

    temperature: float = Field(0.95, alias="temperature")
    top_k: int = Field(20, alias="top_k")
    top_p: float = Field(0.65, alias="top_p")
    max_new_tokens: int = Field(512, alias="max_new_tokens")
    max_seq_len: int = Field(2048, alias="max_seq_len")
    max_input_len: int = Field(2048, alias="max_input_len")
    compress_pos_emb: float = Field(1.0, alias="compress_pos_emb")

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that llama-cpp-python library is installed."""
        try:
            from exllama.model import ExLlama, ExLlamaCache, ExLlamaConfig
            from exllama.tokenizer import ExLlamaTokenizer
            from exllama.generator import ExLlamaGenerator
        except ImportError:
            raise ImportError(
                "Could not import exllama library. "
                "Please install the exllama library to "
                "use this embedding model: pip install git+https://github.com/jllllll/exllama"
            )

        model_directory = values["model_directory"]

        try:
            tokenizer_path = os.path.join(model_directory, "tokenizer.model")
            model_config_path = os.path.join(model_directory, "config.json")
            st_pattern = os.path.join(model_directory, "*.safetensors")
            model_path = glob.glob(st_pattern)[0]

            config = ExLlamaConfig(model_config_path)
            config.model_path = model_path
            config.max_seq_len = values["max_seq_len"]
            config.max_input_len = values["max_input_len"]
            config.compress_pos_emb = values["compress_pos_emb"]
            model = ExLlama(config)

            tokenizer = ExLlamaTokenizer(tokenizer_path)

            cache = ExLlamaCache(model)
            generator = ExLlamaGenerator(model, tokenizer, cache)
            generator.settings.temperature = values["temperature"]
            generator.settings.top_p = values["top_p"]
            generator.settings.top_k = values["top_k"]

            values["llm"] = generator
            values["tokenizer"] = tokenizer
        except Exception as e:
            raise ValueError(
                f"Could not load Llama model from path: {model_directory}. "
                f"Received error {e}"
            )

        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling exllama."""
        params = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_new_tokens": self.max_new_tokens,
        }
        return params

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {**{"model_directory": self.model_directory}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "exllama"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the model and return the output.

        Args:
            prompt: The prompt to use for generation.

        Returns:
            The generated text.

        Example:
            .. code-block:: python

                from langchain.llms import LlamaCpp
                llm = Exllama(model_directory="/path/to/local/llama/")
                llm("This is a prompt.")
        """

        ids = self.tokenizer.encode(prompt)
        remaining_tokens = self.max_seq_len - len(ids[0]) - 1
        if remaining_tokens <= 1:
            raise ValueError(
                f"Prompt is too long. "
                f"Please provide a prompt with fewer than {self.max_seq_len} tokens."
            )
        self.llm.gen_begin(ids)
        self.llm.begin_beam_search()
        num_res_tokens = 0
        res_line = ""
        out_text = ""
        max_response_tokens = self.max_new_tokens
        if max_response_tokens > remaining_tokens:
            max_response_tokens = remaining_tokens
        for i in range(max_response_tokens):
            gen_token = self.llm.beam_search()

            if gen_token.item() == self.tokenizer.eos_token_id:
                break

            num_res_tokens += 1
            text = self.tokenizer.decode(self.llm.sequence_actual[:, -num_res_tokens:][0])
            new_text = text[len(res_line):]

            res_line += new_text
            out_text += new_text

        self.llm.end_beam_search()

        return out_text.strip()

    def get_num_tokens(self, text: str) -> int:
        tokenized_text = self.llm.tokenizer.num_tokens(text.encode("utf-8"))
        return len(tokenized_text)
