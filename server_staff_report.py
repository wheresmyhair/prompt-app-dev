import gradio as gr
import docx
from utils.sysfunc import get_app_version, get_model_version, record_init, parse_text
from os.path import join, basename
from transformers import AutoModel, AutoTokenizer, AutoConfig
import mdtex2html
import time
import json

model_path = "C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm2-6b"
model_config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_path,trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, config=model_config, trust_remote_code=True, device='cuda')
model = model.eval()


# # Override Textbox.postprocess
# def postprocess(self, y):
#     if y is None:
#         return []
#     for i, (message, response) in enumerate(y):
#         y[i] = (
#             None if message is None else mdtex2html.convert((message)),
#             None if response is None else mdtex2html.convert(response),
#         )
#     return y
# gr.components.Textbox.postprocess = postprocess


def clear_content():
    return gr.update(value=None)


def button_action_submit_pre(doc_file):
    record_init(cookies)
    doc = docx.Document(doc_file.name)
    doc.save(join(cookies.value['dir'], basename(doc_file.name)))
    text = ""
    for para in doc.paragraphs:
        text += para.text
    cookies.value.update({'doc_content': text})
    
    cookies.value['doc_summary'].append((time.strftime("%Y%m%d_%H%M%S", time.localtime()),text)) # TODO: add summary
    return {output_doc_content: cookies.value['doc_content'],}
    
def button_action_submit_main(area_text, history, past_key_values, max_length=8192, top_p=0.9, temperature=0.2):
    content = cookies.value['doc_summary'][-1][1]
    print('summary content: ', content)
    for response, history, past_key_values in model.stream_chat(tokenizer, content, history, past_key_values=past_key_values,
                                                                return_past_key_values=True,
                                                                max_length=max_length, top_p=top_p,
                                                                temperature=temperature):
        area_text = parse_text(response)
        yield area_text, history, past_key_values
    cookies.value['final_report'].append((time.strftime("%Y%m%d_%H%M%S", time.localtime()), response))
        
def button_action_submit_post():
    return {button_retry: gr.update(visible=True),
            button_flag: gr.update(visible=True),
            area_download: gr.update(visible=False),
            output_file: gr.update(value=None),}


def button_action_save():
    doc = docx.Document()
    doc.add_paragraph(cookies.value['final_report'][-1][1])
    doc.save(cookies.value['dir_docx_generated'])
    json.dump(cookies.value, open(cookies.value['dir']+'\\cookies.json', 'w'))
    return {area_download: gr.update(visible=True),
            output_file: gr.update(value=cookies.value['dir_docx_generated']),
            button_flag: gr.update(visible=False),
            button_retry: gr.update(visible=False),}


gr_row = lambda: gr.Row()
gr_col = lambda scale: gr.Column(scale=scale)


with gr.Blocks(title="考察报告生成", analytics_enabled=False) as demo:
    # init
    gr.HTML(f"<h1 align=\"center\">考察报告生成 {get_app_version()}</h1>")
    cookies = gr.State({'access_time_abs':None,
                        'access_time': None,
                        'hash': None,
                        'dir': None,
                        'dir_docx_generated': None,
                        'doc_content': None,
                        'doc_summary': [],
                        'final_report': [],})
    history = gr.State([])
    past_key_values = gr.State(None)
    
    # interface
    with gr_row():
        with gr_col(scale=3):
            with gr.Tabs(visible=True, selected=0) as tabs:
                with gr.Tab("考察报告", id=0) as tab_report:
                    with gr_row():
                        output_doc_generate = gr.components.Textbox(label="生成结果",
                                                                    placeholder='请先上传文档',
                                                                    show_copy_button=True,
                                                                    interactive=False)
                    with gr_row():
                        button_flag = gr.Button('保存结果', variant='primary', visible=False)
                        button_retry = gr.Button('重新生成', variant='secondary', visible=False)
                with gr.Tab("上传文档内容预览", id=1) as tab_upload_preview:
                    output_doc_content = gr.components.Textbox(label="文档内容预览", 
                                                            placeholder='请先上传文档', 
                                                            show_copy_button=True, 
                                                            interactive=False)
        with gr_col(scale=2):
            with gr.Accordion("上传区", open=True) as area_input:
                with gr.Row():
                    input_file = gr.components.File(label="述职报告: doc/docx", file_types=['.doc','.docx'])
                with gr.Row():
                    button_submit = gr.Button("提交", variant="primary")
                    button_clear = gr.Button("清除", variant="secondary")
            with gr.Accordion("下载区", open=True, visible=False) as area_download:
                with gr.Row():
                    output_file = gr.components.File(label="考察报告")
            with gr.Accordion("状态栏", open=True) as area_status:
                with gr.Row():
                    info_model_version = gr.Text(label='当前模型', value=f'{get_model_version()}')
                    info_app_version = gr.Text(label='当前应用版本', value=f'{get_app_version()}')

    # button actions
    button_submit.click(fn=button_action_submit_pre,
                        inputs=[input_file],
                        outputs=[output_doc_content],
                        show_progress=True).success(fn=button_action_submit_main,
                                                    inputs=[output_doc_generate, history, past_key_values],
                                                    outputs=[output_doc_generate, history, past_key_values],
                                                    show_progress=True).success(fn=button_action_submit_post,
                                                                                inputs=None, 
                                                                                outputs=[button_flag, button_retry, area_download, output_file],
                                                                                show_progress=False)

    button_clear.click(fn=clear_content, inputs=None, outputs=input_file)

    button_flag.click(fn=button_action_save,
                      inputs=None,
                      outputs=[area_download, output_file,button_flag, button_retry],
                      show_progress=True)
    

if __name__ == '__main__':
    demo.queue().launch(
        server_name='0.0.0.0',
        server_port=7800,
        inbrowser=True,
    )