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
    generator: Any  #: :meta private:
    tokenizer: Any  #: :meta private:
    model: Any   #: :meta private:

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
            values["model"] = model
            values["generator"] = generator
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

        ids = self.tokenizer.encode(prompt, max_seq_len=self.model.config.max_seq_len)
        ids = ids[:, -self.max_input_len:]

        max_new_tokens = self.max_new_tokens

        self.generator.gen_begin_reuse(ids)
        initial_len = self.generator.sequence[0].shape[0]
        has_leading_space = False

        out_text = ""
        for i in range(max_new_tokens):
            token = self.generator.gen_single_token()
            if i == 0 and self.generator.tokenizer.tokenizer.IdToPiece(int(token)).startswith('▁'):
                has_leading_space = True

            decoded_text = self.generator.tokenizer.decode(self.generator.sequence[0][initial_len:])
            if has_leading_space:
                decoded_text = ' ' + decoded_text

            out_text += decoded_text
            if token.item() == self.generator.tokenizer.eos_token_id:
                break

        return out_text

    def get_num_tokens(self, text: str) -> int:
        tokenized_text = self.generator.tokenizer.num_tokens(text.encode("utf-8"))
        return len(tokenized_text)
