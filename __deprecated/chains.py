import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
os.environ["OPENAI_API_KEY"] = "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"
llm = OpenAI(temperature=0)


prompt = PromptTemplate(
    input_variables=['product'],
    template="What info should an instruction of {product} contains?"
)


chain = LLMChain(llm=llm, prompt=prompt)
chain.run(product='VR headset')