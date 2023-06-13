from typing import Any, List, Mapping, Optional, Tuple, Union

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from transformers import AutoTokenizer, AutoModel

class ChatGLM6B(LLM):
    model: Any
    tokenizer: Any
    def __init__(self, model_path: str):
        super().__init__()
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    
    @property
    def _llm_type(self) -> str:
        return "custom: chatglm-6b"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        response, _ = self.model.chat(self.tokenizer, prompt, history=[])
        return response
    
    
llm = ChatGLM6B("C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm-6b")
llm(prompt='你好')