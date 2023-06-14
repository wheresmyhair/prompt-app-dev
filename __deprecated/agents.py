import os

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
os.environ["SERPAPI_API_KEY"] = "ba6695d761ca8d95c58a243e9cb18c43f6f160c21906fde47d8a3ed939398f4b"
os.environ["OPENAI_API_KEY"] = "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"
llm = OpenAI(temperature=0)


tools = load_tools(["serpapi", "llm-math"], llm=llm)


agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


agent.run("What was the high temperature in Celsius in Beijing yesterday?")


from langchain import LLMMathChain

llm_math = LLMMathChain.from_llm(llm, verbose=True)

llm_math.run("96 °F to Celsius")