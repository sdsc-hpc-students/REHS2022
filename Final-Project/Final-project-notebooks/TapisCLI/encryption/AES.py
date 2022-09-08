from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os
from Cryptodome.Random import get_random_bytes
from Crypto import Random
import json


class AESSystem:
    def __init__(self, key):
        self.BLOCK_SIZE = 16
        self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)
        self.unpad = lambda s: s[:-ord(s[len(s)-1:])]
        self.key = str(key)

    def encrypt(self, plain_text):
        key = hashlib.sha256(self.key.encode('utf-8')).digest()
        plain_text = self.pad(plain_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(plain_text.encode()))

    def decrypt(self, encrypted):
        key = hashlib.sha256(self.key.encode('utf-8')).digest()
        encrypted = b64decode(encrypted)
        iv = encrypted[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(encrypted[16:])).decode()

# aes = AESSystem('key')
# encrypted = aes.encrypt(json.dumps({'test':1}))
# print(encrypted)

# decrypted = aes.decrypt(encrypted)
# print(decrypted)