import dkim
from dns import resolver
import re
import hashlib

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


if __name__ == "__main__":
    
    venmo_subject_patterns = [
        r"You paid (.+?) \$(.+)",
        r"(.+?) paid you \$(.+)",
        r"You completed (.+?) \$(.+) charge request",
        r"(.+?) paid your \$(.+) request",
        r"(.+?) requests \$(.+)"
    ]

    # Usage
    texts = [
        "You paid Sachin $1,000",
        "Alex Soong paid you $1,000",
        "You completed Richard $1,000 charge request",
        "Brian paid your $1,000 request",
        "Richard Liang requests $1,000"
    ]

    for text in texts:
        print(match_and_sub(text, venmo_subject_patterns))