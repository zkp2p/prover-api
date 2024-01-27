import dkim
from dns import resolver
import re
import hashlib

def fetch_domain_key(domain, selector='default'):
    try:
        answers = resolver.query(f"{selector}._domainkey.{domain}", 'TXT')
        domain_key = ''.join([s.decode('utf-8') for s in answers[0].strings])
        return domain_key
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


