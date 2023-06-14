from langchain_custom.llm import GLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from utils.save_item import save_splited_text
from langchain.prompts import PromptTemplate

model_path = "C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm-6b"
llm = GLM()
llm.load_model(model_path=model_path)
llm(prompt='你好')

with open("./docs/1.txt", encoding='utf-8') as f:
    personal_report = f.read()
    
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
splited_text = text_splitter.split_text(personal_report)
save_splited_text(splited_text, "./docs/1_splited.txt")

docs = [Document(page_content=x) for x in splited_text]

prompt_template = """对下面的个人述职报告做精简的摘要：

    {report_content}
    
"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["report_content"])

chain = load_summarize_chain(
    llm, 
    chain_type="map_reduce", 
    return_intermediate_steps=True, 
    map_prompt=PROMPT, 
    combine_prompt=PROMPT
)

summ = chain({"input_documents": docs}, return_only_outputs=True)
