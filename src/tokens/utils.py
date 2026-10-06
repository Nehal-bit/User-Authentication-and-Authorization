import random
import uuid
import secrets

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def generate_reset_token():
    return str(uuid.uuid4())