from typing import List,  Optional

from langchain.llms.base import LLM
from transformers import AutoTokenizer, AutoModel, AutoConfig


class GLM(LLM):
    max_token: int = 8192
    temperature: float = 0.95
    top_p: float = 0.8
    tokenizer: object = None
    model: object = None
    model_config: object = None
    history_len: int = 8192
    
    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "Custom model: GLM"
    
    def load_model(self, llm_device="cuda", model_path=None):
        self.model_config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path,trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, config=self.model_config, trust_remote_code=True, device=llm_device)
        self.model = self.model.eval()

    
    def _call(
        self,
        prompt: str,
        history: List[str] = [],
        stop: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        response, _ = self.model.chat(
            self.tokenizer, 
            prompt, 
            history=history[-self.history_len:] if self.history_len > 0 else [],
            max_length=self.max_token,
            temperature=self.temperature if temperature is None else temperature,
            top_p=self.top_p if top_p is None else top_p,
        )
        return response
