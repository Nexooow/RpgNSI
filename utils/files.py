import json

def write_file (file_type, file_name, data):
    with open(f"data/{file_type}/{file_name}", 'w') as f:
        json.dump(data, f)

def read_file (file_type, file_name):
    with open(f"data/{file_type}/{file_name}", 'r') as f:
        return json.load(f)