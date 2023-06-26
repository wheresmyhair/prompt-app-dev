from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from utils.save_item import save_splited_text


def txt_loader(file, chunk_size=1000, chunk_overlap=10, save_splited=None):
    with open(file, encoding='utf-8') as f:
        personal_report = f.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splited_text = text_splitter.split_text(personal_report)
    if save_splited is not None:
        save_splited_text(splited_text, save_splited)
    return [Document(page_content=x) for x in splited_text]


def str_loader(text, chunk_size=1000, chunk_overlap=10):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splited_text = text_splitter.split_text(text)
    return [Document(page_content=x) for x in splited_text]
