from transformers import AutoTokenizer, AutoModel, AutoConfig

model_path = "C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm2-6b"
prompt = "Hello, how are you?"


model_config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_path,trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, config=model_config, trust_remote_code=True, device='cuda')




for response, history in model.stream_chat(
    tokenizer, 
    prompt, 
    history=[],
    max_length=2048,
    temperature=0.2,
    top_p=0.9,
):
    print(response)


