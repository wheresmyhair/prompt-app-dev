import gradio as gr
import docx
from utils.sysfunc import get_current_version

def extract_contents(doc_file):
    doc = docx.Document(doc_file.name)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

def clear_content():
    return gr.update(value=None)

def summary(text):
    return "analyzed: " + text

def extract_and_summary(doc_file):      
    text = extract_contents(doc_file)
    return {output_doc_content: text, 
            output_doc_summary: summary(text), 
            button_retry: gr.update(visible=True), 
            button_save: gr.update(visible=True)}


gr_row = lambda: gr.Row()
gr_col = lambda scale: gr.Column(scale=scale)

with gr.Blocks(title="考察报告生成", analytics_enabled=False) as demo:
    gr.HTML(f"<h1 align=\"center\">考察报告生成 {get_current_version()}</h1>")
    # cookies = gr.State({})
    with gr_row():
        with gr_col(scale=3):
            with gr.Tab("考察报告"):
                with gr_row():
                    output_doc_summary = gr.components.Textbox(label="生成结果")
                with gr_row():
                    button_save = gr.Button('保存', variant='primary', visible=False)
                    button_retry = gr.Button('重新生成', variant='secondary', visible=False)
            with gr.Tab("上传文档内容预览"):
                output_doc_content = gr.components.Textbox(label="文档内容预览")
        with gr_col(scale=2):
            with gr.Accordion("上传区", open=True) as area_input:
                with gr.Row():
                    input_file = gr.components.File(label="述职报告: doc/docx", file_types=['.doc','.docx'])
                with gr.Row():
                    button_submit = gr.Button("提交", variant="primary")
                    button_clear = gr.Button("清除", variant="secondary")
            with gr.Accordion("状态栏", open=True) as area_status:
                with gr.Row():
                    info = gr.Text(label="当前模型",value="123")
                    status = gr.Text(label="当前状态", value="空闲")
                    
    button_submit.click(
        fn=extract_and_summary, 
        inputs=input_file, 
        outputs=[output_doc_content,output_doc_summary, button_save, button_retry], 
        api_name='extractdoc', 
        show_progress=True)
    button_clear.click(fn=clear_content, inputs=None, outputs=input_file)

    
demo.launch(
    server_name='0.0.0.0',
    server_port=7800,
)