# utils/json_handler.py
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, json_string):
    data = json.loads(json_string)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
