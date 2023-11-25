import dkim
from dns import resolver
import re
import hashlib
import requests

def fetch_domain_key(domain, selector='default'):
    try:
        answers = resolver.query(f"{selector}._domainkey.{domain}", 'TXT')
        return answers[0].strings[0].decode('utf-8')
    except Exception as e:
        print(f"Error fetching domain key: {e}")
        return None
 
def validate_dkim(email_raw):
    try:
        d = dkim.DKIM(email_raw.encode('utf-8'))
        valid = d.verify()
        return valid
    except Exception as e:
        print(f"Error during DKIM validation: {e}")
        return False

def sha256_hash(text):
    m = hashlib.sha256()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def match_and_sub(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            log_text = text.replace(match.group(1), '').replace(match.group(2), '')
            return log_text.strip()
    return ""



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



if __name__ == "__main__":
    
    # Fetch domain key
    domain_key = fetch_domain_key('hdfcbank.net', selector='acls01') 
    print(domain_key)
    