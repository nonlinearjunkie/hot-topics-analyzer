import json

def read_json(json_file_path):

    with open(json_file_path) as json_file:
        data = json.load(json_file)

    return data    

