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


def extract_json_values(input_blob, keys):
    # Find the start of the JSON object by looking for '{"id":'
    start_index = input_blob.find('{"id":')
    if start_index == -1:
        # If '{"id":' is not found, return an empty list or handle as needed
        return []

    # Instead of finding the first '}', find the last '}' to ensure capturing the entire JSON object
    end_index = input_blob.rfind('}')
    if end_index == -1:
        # If no closing '}' is found, return an empty list or handle as needed
        return []

    # Extract the JSON string from start_index to end_index+1, inclusive of the closing '}'
    json_str = input_blob[start_index:end_index+1]

    # Parse the JSON string
    data = json.loads(json_str)

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