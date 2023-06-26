from langchain.prompts import PromptTemplate


prompt_template = """请把以下工作摘要改写为员工考察报告,并以"该同志"为主语,力求准确全面,不要分段.\n

工作摘要:"{text}"\n

改写:

"""


PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])