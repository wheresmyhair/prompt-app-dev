from langchain.prompts import PromptTemplate


prompt_template = """请以第三人称视角对以下个人述职报告做准确全面摘要,并以"该员工"为主语.\n

个人述职报告:"{text}"\n

准确全面摘要:

"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])