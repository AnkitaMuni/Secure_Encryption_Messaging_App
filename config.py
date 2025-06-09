import os

SERVER_IP = "127.0.0.1"
PORT = 12345

if not os.path.exists("aes_key.bin"):
    KEY = os.urandom(16)
    with open("aes_key.bin", "wb") as f:
        f.write(KEY)
else:
    with open("aes_key.bin", "rb") as f:
        KEY = f.read()

