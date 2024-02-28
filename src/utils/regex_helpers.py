## Emulating zk-regex in python
import re

def extract_values(input, regex_patterns):
    matched_values = []
    for pattern in regex_patterns:
        match = re.search(pattern, input)
        if match:
            matched_values.append(match.group(1))
    return matched_values
