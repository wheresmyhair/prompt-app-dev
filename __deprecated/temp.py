from langchain.chains.summarize import load_summarize_chain
from langchain.chains import LLMChain
from langchain_custom.staff_report import summarize_prompt, style_trans_prompt

from langchain_custom.staff_report.llm import GLM
from utils.text_loader import txt_loader, str_loader


model_path = "C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm2-6b"
llm = GLM()
llm.load_model(model_path=model_path)


docs = txt_loader("./docs/1.txt", chunk_size=500)
docs = str_loader("12", chunk_size=500)


chain_summ = load_summarize_chain(
    llm, 
    chain_type="map_reduce", 
    return_intermediate_steps=True, 
    map_prompt=summarize_prompt.PROMPT,
    combine_prompt=summarize_prompt.PROMPT,
)

chain_styletrans = LLMChain(llm=llm, prompt=style_trans_prompt.PROMPT)

summ = chain_summ({"input_documents": docs}, return_only_outputs=True)
output = chain_styletrans.run(text=summ['output_text'])


chain_summ_single = LLMChain(llm=llm, prompt=summarize_prompt.PROMPT)
from tqdm import tqdm
summary_paragraphs = ''
for doc in tqdm(docs):
    summary_paragraphs += chain_summ_single.run(doc)
    
chain_summ_single.run(summary_paragraphs)