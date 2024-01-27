import requests

def upload_file_to_slack(channels, token, initial_comment, file_content):
    """Uploads a file to Slack."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "channels": channels,
        "initial_comment": initial_comment,
    }
    response = requests.post(
        "https://slack.com/api/files.upload", 
        headers=headers, 
        params=payload, 
        files=file_content
    )
    return response