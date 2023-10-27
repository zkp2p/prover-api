import dkim
from dns import resolver
import os

def fetch_domain_key(domain, selector='default'):
    try:
        answers = resolver.query(f"{selector}._domainkey.{domain}", 'TXT')
        return answers[0].strings[0].decode('utf-8')
    except Exception as e:
        print(f"Error fetching domain key: {e}")
        return None
 
def validate_dkim(email_raw, domain_key):
    try:
        d = dkim.DKIM(email_raw.encode('utf-8'))
        valid = d.verify()
        return valid
    except Exception as e:
        print(f"Error during DKIM validation: {e}")
        return False

TEST_EMAIL_PATH = "./received_eml/waybill.eml"
print(TEST_EMAIL_PATH)
email_raw_content = None 
with open(TEST_EMAIL_PATH, 'r') as file:
    email_raw_content = file.read()


# Fetch Venmo's domain key (replace 'venmo.com' and 'default' as needed)
domain = 'venmo.com'
selector = 'yzlavq3ml4jl4lt6dltbgmnoftxftkly'  # Replace with Venmo's actual selector
domain_key = fetch_domain_key(domain, selector)
print("domain_key: ", domain_key)
domain_key = 1

print('validating email')

if domain_key:
    # Validate the email
    is_valid = validate_dkim(email_raw_content, domain_key)
    if is_valid:
        print("DKIM validation passed.")
    else:
        print("DKIM validation failed.")
