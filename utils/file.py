import os

def read_txt_files(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"File '{file_name}' not found."