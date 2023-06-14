def save_splited_text(splited_text, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        for text in splited_text:
            f.write(text + '\n\n\n\n\n')