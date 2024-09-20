import json

def compare_json(chat_path:str, python_path:str):
    with open(chat_path, 'r') as f:  
        chat_data = json.load(f)  

    with open(python_path, 'r') as f:  
        python_data = json.load(f)

    print(chat_data)
    print(python_data)

compare_json('ERDFromChat.json', 'ERDFromPython.json')