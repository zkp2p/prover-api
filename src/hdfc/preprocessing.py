

def replace_message_id_with_x_google_original_message_id(email_raw_content):
    message_id_label = "Message-ID: "
    x_google_message_id_label = "X-Google-Original-Message-ID: "

    if message_id_label not in email_raw_content:
        return email_raw_content
    
    message_id_start = email_raw_content.find(message_id_label) + len(message_id_label)
    message_id_end = email_raw_content.find("\n", message_id_start)
    message_id = email_raw_content[message_id_start: message_id_end]
    # print("message_id", message_id)

    # Replace "<message-id>" with "x-message-id" if message id contains "SMTPIN_ADDED_BROKEN@mx.google.com"
    if "SMTPIN_ADDED_BROKEN@mx.google.com" not in message_id and "SMTPIN_ADDED_BROKEN@mx.google.com" not in message_id:
        return email_raw_content

    x_message_id_start = email_raw_content.find(x_google_message_id_label) + len(x_google_message_id_label)
    x_message_id_end = email_raw_content.find("\n", x_message_id_start)
    x_message_id = email_raw_content[x_message_id_start: x_message_id_end]
    # print("x_message_id", x_message_id)

    # Replace "message-id" with "x-message-id"
    return email_raw_content.replace(message_id, x_message_id)