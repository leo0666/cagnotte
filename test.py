"""
import argon2

PH = argon2.PasswordHasher(
    time_cost=4,
    memory_cost=65536,   # 64 Mo
    parallelism=2,
    hash_len=32,
    salt_len=16
)

pwd = "LC!!"

print(PH.hash(pwd))
"""

import secrets

def generate_access_key() -> str:
    return secrets.token_urlsafe(64)

print(generate_access_key())