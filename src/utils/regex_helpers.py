import re
import json

## Emulating zk-regex in python
def extract_regex_values(input, regex_patterns):
    matched_values = []
    for pattern in regex_patterns:
        match = re.search(pattern, input)
        if match:
            matched_values.append(match.group(1))
    return matched_values


def extract_json(input_blob, start_substr, end_substr='}'):

    start_index = input_blob.find(start_substr)
    if start_index == -1:
        return {}

    end_index = input_blob.rfind(end_substr)
    if end_index == -1:
        return {}

    json_str = input_blob[start_index:end_index+len(end_substr)]
    print('json_str', json_str)
    data = json.loads(json_str)
    return data

def extract_json_values(input_blob, keys):
    data = extract_json(input_blob, '{"id":', '}')

    values = []
    for key in keys:
        if isinstance(key, str):
            # If the key is a string, look for it directly in the data
            if key in data:
                values.append(data[key])
        elif isinstance(key, (list, tuple)) and len(key) == 2:
            # If the key is a list or tuple of length 2, navigate to the nested value
            nested_key, inner_key = key
            if nested_key in data and inner_key in data[nested_key]:
                values.append(data[nested_key][inner_key])
    return values
