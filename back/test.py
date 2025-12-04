from passlib.context import CryptContext
from passlib.hash import bcrypt
from passlib.hash import argon2
from argon2 import PasswordHasher
p = "qwerty"

ph = PasswordHasher()

def hashed_pass(password):
    hash_pass = ph.hash(password)
    return hash_pass

hp = hashed_pass(p)

print(hp)
