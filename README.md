# Secure Encryption Messaging App

This is a secure chat application built in Python using **socket programming**. It supports **AES encryption** using a shared key stored in `aes_key.bin`. Both client and server can communicate securely with encrypted messages.

---

## Features

-  AES encryption for secure messaging
-  Python socket server/client
-  Shared key auto-generated and stored in `aes_key.bin`
- 🧪 Easy to run and test on localhost

---

##  AES Key Configuration

The AES key is 16 bytes long (128-bit) and is:
- Automatically generated on the first run
- Stored in `aes_key.bin`
- Loaded by both server and client from `config.py`

---
