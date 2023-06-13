from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("C:\\Users\\59700\\Documents\\_Personals_local\\models\\chatglm-6b", trust_remote_code=True).half().cuda()
response, history = model.chat(tokenizer, "你好", history=[])
print(response)

