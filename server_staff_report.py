import docx
import time
import json
import gradio as gr
import config as cfg
from os.path import join, basename
from utils.sysfunc import get_app_version, get_model_version, record_init, parse_text
from utils.text_loader import str_loader
from utils.save_item import save_docx_from_str
from langchain.chains.summarize import load_summarize_chain
from langchain_custom.staff_report.llm import GLM
from langchain_custom.staff_report import summarize_prompt, style_trans_prompt


llm = GLM()
llm.load_model(model_path=cfg.MODEL_PATH)


def clear_content():
    return {area_input: gr.update(value=None),
            button_flag: gr.update(visible=False),
            button_retry: gr.update(visible=False)}


def button_action_submit_pre(doc_file):
    record_init(cookies)
    doc = docx.Document(doc_file.name)
    print(doc_file.name)
    doc.save(join(cookies.value['dir'], basename(doc_file.name)))
    text = ""
    for para in doc.paragraphs:
        text += para.text
    cookies.value.update({'doc_content': text})
    return {output_doc_content: gr.update(value=cookies.value['doc_content']),
            button_flag: gr.update(visible=False),
            button_retry: gr.update(visible=False)}
    
    
def button_action_submit_main_0(progress=gr.Progress(track_tqdm=True)):
    docs = str_loader(cookies.value['doc_content'], chunk_size=cfg.DOC_LOADER_CHUNK_SIZE)
    chain_summ = load_summarize_chain(
        llm, 
        chain_type="map_reduce", 
        return_intermediate_steps=True, 
        map_prompt=summarize_prompt.PROMPT,
        combine_prompt=summarize_prompt.PROMPT,
    )
    summ = chain_summ({"input_documents": docs}, return_only_outputs=True)
    summ = summ['output_text'].replace('\n', '')
    print('[summary]: ', summ)
    cookies.value['doc_summary'].append((time.strftime("%Y%m%d_%H%M%S", time.localtime()),summ))


def button_action_submit_main_1(area_text, history, past_key_values, max_length=8192, top_p=0.8, temperature=0.95):
    content = cookies.value['doc_summary'][-1][1]
    model_input = style_trans_prompt.PROMPT.format(text=content)
    print('[model input]: ', model_input)
    for response, history, past_key_values in llm.model.stream_chat(llm.tokenizer, model_input, history, past_key_values=past_key_values,
                                                                return_past_key_values=True,
                                                                max_length=max_length, top_p=top_p,
                                                                temperature=temperature):
        # area_text = parse_text(response)
        area_text = response
        yield area_text, history, past_key_values
    cookies.value['final_report'].append((time.strftime("%Y%m%d_%H%M%S", time.localtime()), response))


def button_action_submit_post():
    return {button_retry: gr.update(visible=True),
            button_flag: gr.update(visible=True),
            area_download: gr.update(visible=False),
            output_file: gr.update(value=None),}


def button_action_retry_pre():
    return {button_flag: gr.update(visible=False),
            button_retry: gr.update(visible=False),}


def button_action_save():
    save_docx_from_str(cookies.value['final_report'][-1][1], cookies.value['dir_docx_generated'])
    json.dump(cookies.value, open(cookies.value['dir']+'\\cookies.json', 'w', encoding='utf-8'), ensure_ascii=False)
    return {area_download: gr.update(visible=True),
            output_file: gr.update(value=cookies.value['dir_docx_generated']),
            button_flag: gr.update(visible=False),
            button_retry: gr.update(visible=False),}


gr_row = lambda: gr.Row()
gr_col = lambda scale: gr.Column(scale=scale)


with gr.Blocks(title="考察报告生成",
               analytics_enabled=False, 
               css="footer{visibility:hidden}",) as demo:
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
                                                               interactive=False,
                                                               lines=20,
                                                               max_lines=100)
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
                        outputs=[output_doc_content, button_flag, button_retry],
                        show_progress=True).success(fn=button_action_submit_main_0, 
                                                    inputs=None,
                                                    outputs=[output_doc_generate],
                                                    show_progress=True).success(fn=button_action_submit_main_1,
                                                                                inputs=[output_doc_generate, history, past_key_values],
                                                                                outputs=[output_doc_generate, history, past_key_values],
                                                                                show_progress=True).success(fn=button_action_submit_post,
                                                                                                            inputs=None, 
                                                                                                            outputs=[button_flag, button_retry, area_download, output_file],
                                                                                                            show_progress=False)

    button_clear.click(fn=clear_content, inputs=None, outputs=[input_file, button_flag, button_retry])

    button_flag.click(fn=button_action_save,
                      inputs=None,
                      outputs=[area_download, output_file,button_flag, button_retry],
                      show_progress=True)
    
    button_retry.click(fn=button_action_retry_pre,
                       inputs=None,
                       outputs=[button_flag, button_retry],
                       show_progress=True).success(fn=button_action_submit_main_0,
                                                   inputs=None,
                                                   outputs=[output_doc_generate],
                                                   show_progress=True).success(fn=button_action_submit_main_1,
                                                                               inputs=[output_doc_generate, history, past_key_values],
                                                                               outputs=[output_doc_generate, history, past_key_values],
                                                                               show_progress=True).success(fn=button_action_submit_post,
                                                                                                           inputs=None,
                                                                                                           outputs=[button_flag, button_retry, area_download, output_file],
                                                                                                           show_progress=False)

if __name__ == '__main__':
    demo.queue().launch(
        show_api=False,
        server_name='0.0.0.0',
        server_port=7800,
        inbrowser=True,
    )