import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv('DEV_EMAIL')
SENDER_PASS = os.getenv('DEV_PASS') 
SAMPLE_RECEIVER = os.getenv('SAMPLE_RECEIVER')

print(SENDER_EMAIL)
print(SENDER_PASS)