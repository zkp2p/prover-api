import json

def extract_values_from_response(input_blob, keys):
    # Find the start of the JSON object by looking for '{"id":'
    start_index = input_blob.find('{"id":')
    print('key', start_index)
    if start_index == -1:
        # If '{"id":' is not found, return an empty list or handle as needed
        return []

    # Instead of finding the first '}', find the last '}' to ensure capturing the entire JSON object
    end_index = input_blob.rfind('}')
    print(end_index)
    if end_index == -1:
        # If no closing '}' is found, return an empty list or handle as needed
        return []

    # Extract the JSON string from start_index to end_index+1, inclusive of the closing '}'
    json_str = input_blob[start_index:end_index+1]

    # Parse the JSON string
    data = json.loads(json_str)

    values = []
    for key in keys:
        print(key)
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

# Example usage
input_blob = '''
{"id": 960218004,
  "userId": 55604182,
  "profileId": 41246868,
  "actor": "SENDER",
  "quoteId": "44f17128-9f0b-4b32-973a-cf0203b60402",
  "state": "OUTGOING_PAYMENT_SENT",
  "stateHistory": [
    {
      "state": "WAITING_FOR_PAYMENT",
      "date": 1707407104000
    },
    {
      "state": "INCOMING_PAYMENT_IN_PROGRESS",
      "date": 1707407109000
    },
    {
      "state": "FUNDS_RECEIVED",
      "date": 1707407109000
    },
    {
      "state": "FUNDS_CONVERTED",
      "date": 1707407115000
    },
    {
      "state": "OUTGOING_PAYMENT_SENT",
      "date": 1707407115000
    }
  ],
  "sourceAmount": 0.1,
  "invoiceAmount": 0.1,
  "sourceCurrency": "EUR",
  "targetAmount": 0.1,
  "targetCurrency": "EUR",
  "feeAmount": 0,
  "discountAmount": 0,
  "targetRecipientId": 402863684,
  "refundRecipientId": 403384647,
  "issues": [],
  "paymentReference": "test multiple",
  "fixedRate": 1,
  "feeDetails": {
    "transferwise": 0,
    "payIn": 0,
    "partner": 0
  },
  "availableReceipts": [
    "CONFIRMATION"
  ],
  "externalReferences": [
    {
      "type": "PREFERRED_PAYOUT",
      "value": "BALANCE"
    }
  ]
}
a
'''

# Define keys, including paths for nested values
keys = ["id", "profileId", ["stateHistory", "date"]]  # Example: Extracting "date" will not work directly due to its nested nature and multiple instances

# Extract values
values = extract_values_from_response(input_blob, keys)
print('values', values)
